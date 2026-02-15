"""
Response Composer Agent - Synthesizes outputs from multiple agents into coherent answers.
Final step in Q&A pipeline after all routed agents complete.
"""
from typing import Dict, Any
import json
from .base import ClaudeBaseAgent
from utils.logger import setup_logger

logger = setup_logger(__name__)


class ResponseComposerAgent(ClaudeBaseAgent):
    """
    Response Composer Agent - Creates user-friendly answers from agent outputs.

    Purpose: Synthesize information from multiple agents into coherent response.
    When Called: After all routed agents complete, final step in Q&A pipeline.
    Output: Natural language answer (markdown formatted).
    """

    def __init__(self):
        """Initialize Response Composer Agent."""
        system_prompt = """You are a Response Composer creating user-friendly answers from agent outputs.

TASK: Synthesize the information into a clear, conversational response.

OUTPUT REQUIREMENTS:
- Natural conversational tone (not robotic)
- No markdown formatting, just plain text
- Structure: Brief intro → Key points → Actionable conclusion
- Length: 1-2 paragraphs (If the answers can be answered in a short manner, answer concisely. Only elaborate if necessary)
- Reference specific data points
- End with clear call-to-action
- ONLY answer what the user asked - do not add extra information they didn't request

INPUT DATA:
User Question: {user_question}
Agent Outputs: {agent_outputs_json}

RESPONSE:"""

        super().__init__(
            name="response_composer",
            description="Synthesizes agent outputs into user-friendly answers",
            system_prompt=system_prompt,
            priority=8
        )

        logger.info("Response Composer Agent initialized")

    async def compose(
        self,
        user_question: str,
        agent_outputs: Dict[str, Any]
    ) -> str:
        """
        Compose final response from agent outputs.

        Args:
            user_question: Original user question
            agent_outputs: Dict of agent outputs

        Returns:
            Composed response as markdown text
        """
        try:
            logger.info(f"Composing response for: {user_question}")

            # Build prompt
            agent_outputs_json = json.dumps(agent_outputs, indent=2)

            prompt = f"""Synthesize this information into a clear answer.

USER QUESTION:
{user_question}

AGENT OUTPUTS:
{agent_outputs_json}

Create a natural, helpful response that directly answers the question."""

            # Execute with Claude
            response = await self.execute(
                prompt=prompt,
                max_tokens=1500,
                temperature=0.6  # Balanced creativity
            )

            # Extract composed response
            composed_text = response.get("response", "").strip()

            logger.info(f"Composed response: {len(composed_text)} chars")

            return composed_text

        except Exception as e:
            logger.error(f"Response composition error: {e}")
            return self._get_fallback_response(user_question, agent_outputs, str(e))

    def _get_fallback_response(
        self,
        user_question: str,
        agent_outputs: Dict[str, Any],
        error: str
    ) -> str:
        """Generate fallback response on error."""
        logger.warning(f"Using fallback response due to error: {error}")

        response_parts = [f"I analyzed your question: \"{user_question}\"\n"]

        # Try to extract key information from agent outputs
        if "conversation_retrieval" in agent_outputs:
            results = agent_outputs["conversation_retrieval"].get("results", [])
            if results:
                response_parts.append(f"Found {len(results)} relevant conversations.")

        if "insight" in agent_outputs:
            insights = agent_outputs["insight"].get("insights", [])
            if insights:
                response_parts.append(f"\nKey insights:\n")
                for insight in insights[:3]:
                    response_parts.append(f"- {insight}\n")

        if "recommendation" in agent_outputs:
            recommendations = agent_outputs["recommendation"].get("recommendations", [])
            if recommendations:
                response_parts.append(f"\nRecommendations:\n")
                for rec in recommendations[:3]:
                    response_parts.append(f"{rec.get('priority', '')}. {rec.get('action', 'Review your network')}\n")

        if len(response_parts) == 1:
            response_parts.append("I encountered an issue processing your request. Please try rephrasing your question.")

        return "".join(response_parts)
