"""
Insight Agent - Analyzes patterns and generates insights across all networking data.
"""
from typing import Dict, Any, Optional
import json
import re
from .base import ClaudeBaseAgent
from utils.logger import setup_logger

logger = setup_logger(__name__)


class InsightAgent(ClaudeBaseAgent):
    """
    Insight Agent - Analyzes patterns and trends across networking data.

    Purpose: Generate insights from aggregated data (topics, companies, sentiment, etc.).
    When Called: As determined by Query Router, for pattern/trend questions.
    Output: JSON with insights, recommendations, and key metrics.
    """

    def __init__(self):
        """Initialize Insight Agent."""
        system_prompt = """You are an Insight Agent analyzing networking data patterns.

TASK: Analyze aggregated data and answer the user's question with insights.

OUTPUT FORMAT (JSON):
{
  "insights": [
    "Insight 1 (1 sentence)",
    "Insight 2 (1 sentence)",
    "Insight 3 (1 sentence)"
  ],
  "recommendations": [
    "Recommendation 1 (1 sentence)",
    "Recommendation 2 (1 sentence)"
  ],
  "key_metric": {
    "label": "Most discussed topic",
    "value": "AI (65% of conversations)"
  }
}

ANALYSIS APPROACH:
1. Look for patterns in the data (frequency, trends, correlations)
2. Identify notable insights that answer the question
3. Provide actionable recommendations based on insights
4. Highlight the most important metric

DATA:
{aggregated_data}

QUESTION: {user_question}

JSON OUTPUT:"""

        super().__init__(
            name="insight",
            description="Analyzes patterns and trends across networking data",
            system_prompt=system_prompt,
            priority=6
        )

        logger.info("Insight Agent initialized")

    async def execute(
        self,
        user_question: str,
        user_id: str,
        conversation_data: Optional[list] = None,
        time_range: str = "all_time",
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate insights from conversation data.

        Args:
            user_question: User's question
            user_id: User identifier
            conversation_data: List of conversation dicts from GCS (passed by orchestrator)
            time_range: Time range for analysis ("last_30_days", "all_time")

        Returns:
            Dict with insights, recommendations, and key metrics
        """
        try:
            print(f"\n    [INSIGHT_AGENT] Generating insights for: '{user_question}'")
            print(f"    [INSIGHT_AGENT] user_id: {user_id}")
            print(f"    [INSIGHT_AGENT] Conversation data provided: {conversation_data is not None}")
            if conversation_data:
                print(f"    [INSIGHT_AGENT] Number of conversations: {len(conversation_data)}")
            logger.info(f"Generating insights for: {user_question}")

            # Build conversation summaries for analysis
            conversation_summaries = ""
            if conversation_data:
                for i, conv in enumerate(conversation_data, 1):
                    title = conv.get("title", f"Conversation {i}")
                    transcript = conv.get("transcript", "")
                    # Truncate for insight analysis
                    if len(transcript) > 2000:
                        transcript = transcript[:2000] + "... [truncated]"
                    conversation_summaries += f"\n--- {title} ---\n{transcript}\n"

            # Build prompt
            prompt = f"""Analyze this networking/event conversation data and answer the question.

CONVERSATION DATA:
{conversation_summaries if conversation_summaries else "No conversation data available."}

USER QUESTION: {user_question}

Generate insights and recommendations as JSON."""

            # Execute with Claude
            print(f"    [INSIGHT_AGENT] Calling Claude API (model: {self.model})...")
            response = await super().execute(
                prompt=prompt,
                max_tokens=1000,
                temperature=0.4
            )
            print(f"    [INSIGHT_AGENT] Claude response status: {response.get('status', 'unknown')}")

            # Parse JSON response
            result_text = response.get("response", "{}")
            print(f"    [INSIGHT_AGENT] Raw response: {result_text[:200]}")
            insights = self._parse_json_response(result_text)

            # Validate
            insights = self._validate_insights(insights)

            print(f"    [INSIGHT_AGENT] Generated {len(insights.get('insights', []))} insights")
            logger.info(f"Generated {len(insights.get('insights', []))} insights")

            return insights

        except Exception as e:
            print(f"    [INSIGHT_AGENT] ERROR: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            logger.error(f"Insight generation error: {e}")
            return {
                "insights": ["Unable to generate insights at this time"],
                "recommendations": [],
                "key_metric": {"label": "Error", "value": str(e)},
                "error": str(e)
            }

    async def _fetch_and_aggregate_data(
        self,
        user_id: str,
        time_range: str
    ) -> Dict[str, Any]:
        """
        Fetch and aggregate networking data.
        TODO: Implement database queries and aggregation.
        """
        # Placeholder aggregated data
        return {
            "total_conversations": 23,
            "total_people": 18,
            "topic_frequency": {
                "AI": 15,
                "Machine Learning": 12,
                "Healthcare": 8,
                "Startups": 6
            },
            "company_frequency": {
                "Google": 5,
                "Microsoft": 3,
                "Startup X": 2
            },
            "sentiment_distribution": {
                "positive": 15,
                "neutral": 6,
                "negative": 2
            },
            "goal_alignment_avg": 0.72
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

    def _validate_insights(self, insights: Dict[str, Any]) -> Dict[str, Any]:
        """Validate insights structure."""
        if "insights" not in insights:
            insights["insights"] = []
        if "recommendations" not in insights:
            insights["recommendations"] = []
        if "key_metric" not in insights:
            insights["key_metric"] = {"label": "No metric", "value": "N/A"}

        return insights
