# ABOUTME: Multi-agent orchestrator for coordinating agent execution with priority handling.
# ABOUTME: Manages agent registration, sequential/parallel execution, and execution history tracking.
from typing import Dict, List, Any, Optional, AsyncIterator, Union
import asyncio
from datetime import datetime
from .base import ClaudeBaseAgent
from utils.logger import setup_logger

logger = setup_logger(__name__)


class AgentOrchestrator:
    """Coordinates execution of multiple agents with priority handling."""

    def __init__(self):
        """Initialize orchestrator."""
        self.agents: Dict[str, ClaudeBaseAgent] = {}
        self.agent_priorities: Dict[str, int] = {}
        self.execution_history: List[Dict[str, Any]] = []

        logger.info("Agent Orchestrator initialized")

    def register_agent(self, agent: ClaudeBaseAgent, priority: Optional[int] = None) -> None:
        """
        Register an agent with the orchestrator.

        Args:
            agent: Agent to register
            priority: Optional priority override (1 = highest)
        """
        self.agents[agent.name] = agent
        agent_priority = priority if priority is not None else agent.priority
        self.agent_priorities[agent.name] = agent_priority

        logger.info(
            f"Registered agent: {agent.name} "
            f"(priority: {agent_priority}, total agents: {len(self.agents)})"
        )

    def unregister_agent(self, agent_name: str) -> bool:
        """
        Unregister an agent.

        Args:
            agent_name: Name of agent to unregister

        Returns:
            True if agent was unregistered, False if not found
        """
        if agent_name in self.agents:
            del self.agents[agent_name]
            del self.agent_priorities[agent_name]
            logger.info(f"Unregistered agent: {agent_name}")
            return True
        return False

    def get_agent(self, agent_name: str) -> Optional[ClaudeBaseAgent]:
        """
        Get an agent by name.

        Args:
            agent_name: Agent name

        Returns:
            Agent instance or None
        """
        return self.agents.get(agent_name)

    def list_agents(self) -> List[Dict[str, Any]]:
        """
        List all registered agents.

        Returns:
            List of agent information sorted by priority
        """
        agents_info = []
        for agent_name, agent in self.agents.items():
            agents_info.append({
                "name": agent.name,
                "description": agent.description,
                "priority": self.agent_priorities[agent_name],
                "model": agent.model,
                "available": True,
                "stats": agent.get_stats()
            })

        # Sort by priority (1 = highest)
        agents_info.sort(key=lambda x: x["priority"])
        return agents_info

    async def execute_agent(
        self,
        agent_name: str,
        prompt: str,
        context: Optional[Dict[str, Any]] = None,
        stream: bool = False,
        **kwargs
    ) -> Union[AsyncIterator[Dict[str, Any]], Dict[str, Any]]:
        """
        Execute a specific agent.

        Args:
            agent_name: Name of agent to execute
            prompt: Prompt for the agent
            context: Optional context
            stream: Whether to stream response
            **kwargs: Additional arguments for agent execution

        Returns:
            Agent response

        Raises:
            ValueError: If agent not found
        """
        agent = self.get_agent(agent_name)
        if not agent:
            raise ValueError(f"Agent '{agent_name}' not found")

        logger.info(f"Executing agent: {agent_name}")
        start_time = datetime.utcnow()

        try:
            result = await agent.execute(
                prompt=prompt,
                context=context,
                stream=stream,
                **kwargs
            )

            # Record execution
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            self._record_execution(
                agent_name=agent_name,
                execution_time=execution_time,
                status="success"
            )

            return result

        except Exception as e:
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            self._record_execution(
                agent_name=agent_name,
                execution_time=execution_time,
                status="error",
                error=str(e)
            )
            raise

    async def execute_agents_parallel(
        self,
        agent_requests: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Execute multiple agents in parallel.

        Args:
            agent_requests: List of agent request dictionaries with keys:
                - agent_name: Name of agent
                - prompt: Prompt for agent
                - context: Optional context
                - Other agent-specific parameters

        Returns:
            List of agent responses
        """
        logger.info(f"Executing {len(agent_requests)} agents in parallel")

        # Create tasks
        tasks = []
        for request in agent_requests:
            agent_name = request.get("agent_name")
            prompt = request.get("prompt")
            context = request.get("context")

            # Get agent-specific parameters
            kwargs = {k: v for k, v in request.items()
                      if k not in ["agent_name", "prompt", "context"]}

            task = self.execute_agent(
                agent_name=agent_name,
                prompt=prompt,
                context=context,
                stream=False,
                **kwargs
            )
            tasks.append(task)

        # Execute all tasks
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Process results
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Agent {agent_requests[i]['agent_name']} failed: {result}")
                processed_results.append({
                    "agent_name": agent_requests[i]["agent_name"],
                    "status": "error",
                    "error": str(result)
                })
            else:
                processed_results.append(result)

        return processed_results

    async def execute_agents_sequential(
        self,
        agent_requests: List[Dict[str, Any]],
        stop_on_error: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Execute multiple agents sequentially (respecting priority order).

        Args:
            agent_requests: List of agent request dictionaries
            stop_on_error: Whether to stop execution on first error

        Returns:
            List of agent responses
        """
        # Sort by agent priority
        sorted_requests = sorted(
            agent_requests,
            key=lambda x: self.agent_priorities.get(x["agent_name"], 99)
        )

        logger.info(f"Executing {len(sorted_requests)} agents sequentially")

        results = []
        for request in sorted_requests:
            agent_name = request.get("agent_name")
            prompt = request.get("prompt")
            context = request.get("context")

            # Get agent-specific parameters
            kwargs = {k: v for k, v in request.items()
                      if k not in ["agent_name", "prompt", "context"]}

            try:
                result = await self.execute_agent(
                    agent_name=agent_name,
                    prompt=prompt,
                    context=context,
                    stream=False,
                    **kwargs
                )
                results.append(result)

            except Exception as e:
                logger.error(f"Agent {agent_name} failed: {e}")
                error_result = {
                    "agent_name": agent_name,
                    "status": "error",
                    "error": str(e)
                }
                results.append(error_result)

                if stop_on_error:
                    logger.warning("Stopping execution due to error")
                    break

        return results

    def _record_execution(
        self,
        agent_name: str,
        execution_time: float,
        status: str,
        error: Optional[str] = None
    ):
        """Record agent execution in history."""
        record = {
            "agent_name": agent_name,
            "timestamp": datetime.utcnow().isoformat(),
            "execution_time": execution_time,
            "status": status
        }

        if error:
            record["error"] = error

        self.execution_history.append(record)

        # Keep only last 1000 executions
        if len(self.execution_history) > 1000:
            self.execution_history = self.execution_history[-1000:]

    def get_execution_history(
        self,
        agent_name: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get execution history.

        Args:
            agent_name: Optional filter by agent name
            limit: Maximum number of records to return

        Returns:
            List of execution records
        """
        history = self.execution_history

        if agent_name:
            history = [h for h in history if h["agent_name"] == agent_name]

        return history[-limit:]

    def get_stats(self) -> Dict[str, Any]:
        """Get orchestrator statistics."""
        total_success = sum(1 for h in self.execution_history if h["status"] == "success")
        total_errors = sum(1 for h in self.execution_history if h["status"] == "error")
        
        avg_exec_time = 0.0
        if self.execution_history:
            avg_exec_time = sum(h["execution_time"] for h in self.execution_history) / len(self.execution_history)

        return {
            "total_agents": len(self.agents),
            "total_executions": len(self.execution_history),
            "total_success": total_success,
            "total_errors": total_errors,
            "average_execution_time": round(avg_exec_time, 3),
            "agents": self.list_agents()
        }


# Global orchestrator instance
orchestrator = AgentOrchestrator()
