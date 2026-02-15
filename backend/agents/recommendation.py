"""
Recommendation Agent - Suggests next actions based on networking data.
"""
from typing import Dict, Any, Optional
import json
import re
from .base import ClaudeBaseAgent
from utils.logger import setup_logger

logger = setup_logger(__name__)


class RecommendationAgent(ClaudeBaseAgent):
    """
    Recommendation Agent - Provides actionable networking advice.

    Purpose: Suggest next actions (who to follow up with, introduce, etc.).
    When Called: As determined by Query Router, for "what should I do" questions.
    Output: JSON with prioritized recommendations.
    """

    def __init__(self):
        """Initialize Recommendation Agent."""
        system_prompt = """You are a Recommendation Agent providing actionable networking advice.

TASK: Generate 3-5 prioritized recommendations based on the data.

OUTPUT FORMAT (JSON ONLY):
{
  "recommendations": [
    {
      "priority": 1,
      "action": "Short action description (max 10 words)",
      "rationale": "Why this matters (1 sentence)",
      "next_steps": "Concrete next steps (1 sentence)"
    }
  ]
}

PRIORITIZATION CRITERIA:
1. Pending action items (high priority)
2. High-value contacts not followed up with
3. Conversations with positive sentiment and goal alignment
4. Time-sensitive opportunities
5. Relationships going cold (>2 weeks no contact)

CONTEXT:
{context_data}

QUESTION: {user_question}

JSON OUTPUT:"""

        super().__init__(
            name="recommendation",
            description="Suggests next actions for networking",
            system_prompt=system_prompt,
            priority=7
        )

        logger.info("Recommendation Agent initialized")

    async def execute(
        self,
        user_question: str,
        user_id: str,
        context_from_other_agents: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate recommendations based on data and context.

        Args:
            user_question: User's question
            user_id: User identifier
            context_from_other_agents: Context from previous agents

        Returns:
            Dict with prioritized recommendations
        """
        try:
            logger.info(f"Generating recommendations for: {user_question}")

            # Build prompt with context
            context_json = json.dumps(context_from_other_agents or {}, indent=2)

            prompt = f"""Generate recommendations based on this context.

CONTEXT DATA:
{context_json}

USER QUESTION: {user_question}

Provide 3-5 prioritized actionable recommendations as JSON."""

            # Execute with Claude
            response = await super().execute(
                prompt=prompt,
                max_tokens=1000,
                temperature=0.5
            )

            # Parse JSON response
            result_text = response.get("response", "{}")
            recommendations = self._parse_json_response(result_text)

            # Validate
            recommendations = self._validate_recommendations(recommendations)

            logger.info(f"Generated {len(recommendations.get('recommendations', []))} recommendations")

            return recommendations

        except Exception as e:
            logger.error(f"Recommendation generation error: {e}")
            return {
                "recommendations": [{
                    "priority": 1,
                    "action": "Review recent conversations",
                    "rationale": "Unable to generate specific recommendations",
                    "next_steps": "Check your networking dashboard for pending items"
                }],
                "error": str(e)
            }

    def _parse_json_response(self, response_text: str) -> Dict[str, Any]:
        """Parse JSON from Claude response."""
        response_text = response_text.strip()

        # Remove markdown code blocks
        if response_text.startswith("```"):
            lines = response_text.split("\n")
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].strip().startswith("```"):
                lines = lines[:-1]
            response_text = "\n".join(lines).strip()

        try:
            return json.loads(response_text)
        except json.JSONDecodeError as e:
            logger.error(f"JSON parse error: {e}")
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                try:
                    return json.loads(json_match.group())
                except:
                    pass
            raise

    def _validate_recommendations(self, recommendations: Dict[str, Any]) -> Dict[str, Any]:
        """Validate recommendations structure."""
        if "recommendations" not in recommendations:
            recommendations["recommendations"] = []

        # Validate each recommendation
        for i, rec in enumerate(recommendations["recommendations"], 1):
            if "priority" not in rec:
                rec["priority"] = i
            if "action" not in rec:
                rec["action"] = "Follow up"
            if "rationale" not in rec:
                rec["rationale"] = "Recommended action"
            if "next_steps" not in rec:
                rec["next_steps"] = "Take action"

        # Limit to 5 recommendations
        recommendations["recommendations"] = recommendations["recommendations"][:5]

        return recommendations
