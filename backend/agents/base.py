"""
Base agent wrapper for Claude-powered agents.
"""
from anthropic import Anthropic, AsyncAnthropic
from typing import AsyncIterator, Dict, Any, Optional, List, Union
from datetime import datetime
import asyncio
from config import settings
from utils.logger import setup_logger

logger = setup_logger(__name__)


class ClaudeBaseAgent:
    """Base class for all Claude-powered agents."""

    def __init__(
        self,
        name: str,
        description: str,
        system_prompt: str,
        priority: int = 5,
        model: str = None,
        tools: Optional[List[Dict[str, Any]]] = None
    ):
        """
        Initialize Claude agent.

        Args:
            name: Agent name
            description: Agent description
            system_prompt: System prompt for the agent
            priority: Agent priority (1 = highest)
            model: Claude model to use
            tools: Optional list of tools for the agent
        """
        self.name = name
        self.description = description
        self.system_prompt = system_prompt
        self.priority = priority
        self.model = model or settings.default_agent_model
        self.tools = tools or []

        # Initialize Anthropic client
        self.client = AsyncAnthropic(api_key=settings.anthropic_api_key)

        # Agent statistics
        self.total_executions = 0
        self.total_tokens_used = 0
        self.avg_execution_time = 0.0

        logger.info(f"Initialized agent: {self.name} (priority: {self.priority})")

    async def execute(
        self,
        prompt: str,
        context: Optional[Dict[str, Any]] = None,
        max_tokens: int = 4096,
        temperature: float = 1.0,
        stream: bool = False
    ) -> Union[AsyncIterator[Dict[str, Any]], Dict[str, Any]]:
        """
        Execute the agent with a given prompt.

        Args:
            prompt: User prompt
            context: Optional context dictionary
            max_tokens: Maximum tokens in response
            temperature: Sampling temperature
            stream: Whether to stream the response

        Returns:
            Agent response (streaming or complete)
        """
        start_time = datetime.utcnow()

        # Build messages
        messages = [{"role": "user", "content": prompt}]

        # Add context if provided
        if context:
            context_str = self._format_context(context)
            messages[0]["content"] = f"{context_str}\n\n{prompt}"

        try:
            print(f"      [BASE_AGENT:{self.name}] Executing with prompt length: {len(prompt)}")
            print(f"      [BASE_AGENT:{self.name}] Model: {self.model}, max_tokens: {max_tokens}, temp: {temperature}")
            print(f"      [BASE_AGENT:{self.name}] API key present: {bool(self.client.api_key)}")
            print(f"      [BASE_AGENT:{self.name}] API key prefix: {str(self.client.api_key)[:12]}..." if self.client.api_key else "      [BASE_AGENT] No API key!")
            logger.info(f"Executing agent {self.name} with prompt length: {len(prompt)}")

            if stream:
                return self._execute_streaming(
                    messages=messages,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    start_time=start_time
                )
            else:
                result = await self._execute_complete(
                    messages=messages,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    start_time=start_time
                )
                print(f"      [BASE_AGENT:{self.name}] Execution completed successfully")
                return result

        except Exception as e:
            print(f"      [BASE_AGENT:{self.name}] EXECUTION ERROR: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            logger.error(f"Error executing agent {self.name}: {e}")
            raise

    async def _execute_complete(
        self,
        messages: List[Dict[str, str]],
        max_tokens: int,
        temperature: float,
        start_time: datetime
    ) -> Dict[str, Any]:
        """Execute agent and return complete response."""
        # Build API call parameters
        api_params = {
            "model": self.model,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "system": self.system_prompt,
            "messages": messages,
        }

        # Only include tools if they exist
        if self.tools:
            api_params["tools"] = self.tools

        response = await self.client.messages.create(**api_params)

        # Update statistics
        execution_time = (datetime.utcnow() - start_time).total_seconds()
        self._update_stats(execution_time, response.usage.input_tokens + response.usage.output_tokens)

        # Extract text content
        content_text = ""
        for block in response.content:
            if hasattr(block, 'text'):
                content_text += block.text

        logger.info(
            f"Agent {self.name} completed execution in {execution_time:.2f}s "
            f"(tokens: {response.usage.input_tokens + response.usage.output_tokens})"
        )

        return {
            "agent_name": self.name,
            "response": content_text,
            "status": "completed",
            "execution_time": execution_time,
            "tokens_used": {
                "input": response.usage.input_tokens,
                "output": response.usage.output_tokens,
                "total": response.usage.input_tokens + response.usage.output_tokens
            },
            "model": self.model,
            "stop_reason": response.stop_reason
        }

    async def _execute_streaming(
        self,
        messages: List[Dict[str, str]],
        max_tokens: int,
        temperature: float,
        start_time: datetime
    ) -> AsyncIterator[Dict[str, Any]]:
        """Execute agent with streaming response."""
        # Build API call parameters
        api_params = {
            "model": self.model,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "system": self.system_prompt,
            "messages": messages,
        }

        # Only include tools if they exist
        if self.tools:
            api_params["tools"] = self.tools

        async with self.client.messages.stream(**api_params) as stream:
            total_tokens = 0
            async for text in stream.text_stream:
                yield {
                    "agent_name": self.name,
                    "type": "content_chunk",
                    "content": text,
                    "status": "streaming"
                }

            # Get final message
            message = await stream.get_final_message()

            # Update statistics
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            total_tokens = message.usage.input_tokens + message.usage.output_tokens
            self._update_stats(execution_time, total_tokens)

            # Send completion event
            yield {
                "agent_name": self.name,
                "type": "completion",
                "status": "completed",
                "execution_time": execution_time,
                "tokens_used": {
                    "input": message.usage.input_tokens,
                    "output": message.usage.output_tokens,
                    "total": total_tokens
                },
                "stop_reason": message.stop_reason
            }

            logger.info(
                f"Agent {self.name} completed streaming in {execution_time:.2f}s "
                f"(tokens: {total_tokens})"
            )

    def _format_context(self, context: Dict[str, Any]) -> str:
        """Format context dictionary for inclusion in prompt."""
        context_parts = ["<context>"]
        for key, value in context.items():
            context_parts.append(f"<{key}>{value}</{key}>")
        context_parts.append("</context>")
        return "\n".join(context_parts)

    def _update_stats(self, execution_time: float, tokens_used: int):
        """Update agent execution statistics."""
        self.total_executions += 1
        self.total_tokens_used += tokens_used

        # Update average execution time
        if self.total_executions == 1:
            self.avg_execution_time = execution_time
        else:
            self.avg_execution_time = (
                (self.avg_execution_time * (self.total_executions - 1) + execution_time)
                / self.total_executions
            )

    def get_stats(self) -> Dict[str, Any]:
        """Get agent statistics."""
        return {
            "agent_name": self.name,
            "description": self.description,
            "priority": self.priority,
            "model": self.model,
            "total_executions": self.total_executions,
            "total_tokens_used": self.total_tokens_used,
            "avg_execution_time": self.avg_execution_time
        }

    def __repr__(self) -> str:
        return f"<ClaudeAgent: {self.name} (priority: {self.priority})>"
