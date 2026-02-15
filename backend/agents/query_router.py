"""
Query Router Agent - Analyzes user questions and decides which agents to call for Q&A.
Runs when user asks a question in web dashboard.
"""
from typing import Dict, Any, List, Optional
import json
import re
from .base import ClaudeBaseAgent
from utils.logger import setup_logger

logger = setup_logger(__name__)


class QueryRouterAgent(ClaudeBaseAgent):
    """
    Query Router Agent - Routes user questions to appropriate agents.

    Purpose: Analyze user question and decide which agents should be called.
    When Called: When user asks a question in web dashboard.
    Output: JSON with agents_needed, execution_mode, question_type.
    """

    def __init__(self):
        """Initialize Query Router Agent."""
        system_prompt = """You are a Query Router Agent. Your job is to analyze user questions and decide which specialized agents should be called to answer.

AVAILABLE AGENTS:
1. conversation_retrieval - Search and fetch specific conversations/quotes
2. insight - Analyze patterns, trends, statistics across all data
3. followup - Information about follow-up messages and their status
4. recommendation - Suggest next actions, prioritize contacts

OUTPUT FORMAT (JSON ONLY):
{
  "agents_needed": ["agent1", "agent2"],
  "execution_mode": "parallel" or "sequential",
  "question_type": "factual" or "analytical" or "recommendation" or "comparison",
  "reasoning": "Brief explanation of routing decision (1 sentence)"
}

ROUTING RULES:
- Factual questions ("What did Alice say?") → conversation_retrieval only
- Pattern questions ("What topics come up most?") → insight only
- Prioritization ("Who should I contact?") → conversation_retrieval + recommendation
- Comparison ("Compare Alice vs Bob") → conversation_retrieval + insight
- Complex multi-part → multiple agents, sequential execution
- If unsure, default to conversation_retrieval

USER QUESTION: {user_question}

JSON OUTPUT:"""

        super().__init__(
            name="query_router",
            description="Routes user questions to appropriate specialized agents",
            system_prompt=system_prompt,
            priority=2
        )

        logger.info("Query Router Agent initialized")

    async def route(self, user_question: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Route user question to appropriate agents.

        Args:
            user_question: User's natural language question
            context: Optional context (user_id, recent_events, etc.)

        Returns:
            Routing decision with agents_needed, execution_mode, question_type
        """
        try:
            logger.info(f"Routing question: {user_question}")

            # Build prompt
            prompt = user_question

            # Execute with Claude
            response = await self.execute(
                prompt=prompt,
                context=context,
                max_tokens=500,
                temperature=0.2  # Low temperature for consistent routing
            )

            # Parse JSON response
            result_text = response.get("response", "{}")
            routing = self._parse_json_response(result_text)

            # Validate routing
            routing = self._validate_routing(routing)

            logger.info(f"Routing decision: {routing['agents_needed']} ({routing['execution_mode']})")

            return routing

        except Exception as e:
            logger.error(f"Query router error: {e}, defaulting to conversation_retrieval")
            return {
                "agents_needed": ["conversation_retrieval"],
                "execution_mode": "parallel",
                "question_type": "factual",
                "reasoning": f"Routing failed, using default: {str(e)}"
            }

    def _parse_json_response(self, response_text: str) -> Dict[str, Any]:
        """Parse JSON from Claude response."""
        # Clean response
        response_text = response_text.strip()

        # Remove markdown code blocks
        if response_text.startswith("```"):
            lines = response_text.split("\n")
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].strip().startswith("```"):
                lines = lines[:-1]
            response_text = "\n".join(lines).strip()

        # Try to parse JSON
        try:
            return json.loads(response_text)
        except json.JSONDecodeError as e:
            logger.error(f"JSON parse error: {e}")
            # Try to extract JSON from text
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                try:
                    return json.loads(json_match.group())
                except:
                    pass
            raise

    def _validate_routing(self, routing: Dict[str, Any]) -> Dict[str, Any]:
        """Validate routing decision."""
        valid_agents = ["conversation_retrieval", "insight", "followup", "recommendation"]
        valid_modes = ["parallel", "sequential"]
        valid_types = ["factual", "analytical", "recommendation", "comparison"]

        # Validate agents_needed
        if "agents_needed" not in routing or not routing["agents_needed"]:
            routing["agents_needed"] = ["conversation_retrieval"]

        # Filter invalid agents
        routing["agents_needed"] = [
            agent for agent in routing["agents_needed"]
            if agent in valid_agents
        ]

        # If no valid agents, default to conversation_retrieval
        if not routing["agents_needed"]:
            routing["agents_needed"] = ["conversation_retrieval"]

        # Validate execution_mode
        if "execution_mode" not in routing or routing["execution_mode"] not in valid_modes:
            # Default: parallel if 1 agent, sequential if multiple
            routing["execution_mode"] = "parallel" if len(routing["agents_needed"]) == 1 else "sequential"

        # Validate question_type
        if "question_type" not in routing or routing["question_type"] not in valid_types:
            routing["question_type"] = "factual"

        # Ensure reasoning exists
        if "reasoning" not in routing:
            routing["reasoning"] = "Routing based on question analysis"

        return routing
