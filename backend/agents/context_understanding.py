"""
Context Understanding Agent - Extracts structured entities, topics, and insights from conversations.
Runs once per conversation after event ends, after upload to cloud.
"""
from typing import Dict, Any, List, Optional
import json
import re
from .base import ClaudeBaseAgent
from utils.logger import setup_logger

logger = setup_logger(__name__)


class ContextUnderstandingAgent(ClaudeBaseAgent):
    """
    Context Understanding Agent - Extracts structured information from conversations.

    Purpose: Extract entities, topics, and insights from full conversations.
    When Called: After event ends, once per conversation, after upload to cloud.
    Output: Structured JSON with people, topics, action items, etc.
    """

    def __init__(self):
        """Initialize Context Understanding Agent."""
        system_prompt = """You are a Context Understanding Agent analyzing networking conversations.

TASK: Extract structured information from this conversation.

OUTPUT FORMAT (JSON ONLY):
{
  "people": [
    {
      "speaker_id": "Speaker 1",
      "name": "First Last" or null,
      "role": "Job title" or null,
      "company": "Company name" or null,
      "email": "email@example.com" or null,
      "linkedin": "linkedin.com/in/username" or null
    }
  ],
  "companies_mentioned": ["Company1", "Company2"],
  "topics_discussed": ["Topic1", "Topic2", "Topic3"],
  "technologies_mentioned": ["Python", "TensorFlow"],
  "action_items": [
    {
      "assigned_to": "user" or "other_party",
      "action": "Short action description (max 8 words)",
      "deadline": "this week" or "next month" or null,
      "priority": "high" or "medium" or "low"
    }
  ],
  "key_interests": ["Interest area 1", "Interest area 2"],
  "pain_points_mentioned": ["Pain point 1"],
  "conversation_summary": "1-2 sentence summary of conversation",
  "sentiment": "positive" or "neutral" or "negative",
  "goal_alignment": {
    "matches_user_goals": true or false,
    "which_goals": ["Find investors"],
    "alignment_score": 0.0 to 1.0
  }
}

RULES:
1. Extract ALL people mentioned, not just speakers
2. Topics should be specific (not generic like "business")
3. Action items must be concrete and actionable
4. Summary max 2 sentences
5. Be concise: action items max 8 words each
6. Output ONLY valid JSON, no markdown, no explanation

USER GOALS: {user_goals}

CONVERSATION:
{full_transcript}

JSON OUTPUT:"""

        super().__init__(
            name="context_understanding",
            description="Extracts structured entities and insights from conversations",
            system_prompt=system_prompt,
            priority=3
        )

        logger.info("Context Understanding Agent initialized")

    async def analyze_conversation(
        self,
        conversation_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Extract entities and insights from conversation.

        Args:
            conversation_data: Dictionary with:
                - conversation_id: str
                - full_transcript: str
                - speaker_labels: List[str]
                - duration_minutes: int
                - user_goals: List[str]
                - event_context: Dict (event_name, event_date, location)

        Returns:
            Structured data with people, topics, action items, etc.
        """
        try:
            logger.info(f"Context Understanding analyzing conversation {conversation_data.get('conversation_id')}")

            # Build prompt with conversation data
            user_goals = conversation_data.get('user_goals', ['Network and build connections'])
            full_transcript = conversation_data.get('full_transcript', '')

            prompt = f"""Analyze this networking conversation.

CONVERSATION ID: {conversation_data.get('conversation_id', 'unknown')}
DURATION: {conversation_data.get('duration_minutes', 0)} minutes
SPEAKERS: {', '.join(conversation_data.get('speaker_labels', []))}
EVENT: {conversation_data.get('event_context', {}).get('event_name', 'Unknown Event')}

USER GOALS:
{', '.join(user_goals)}

FULL TRANSCRIPT:
{full_transcript}

Extract structured information and return as JSON."""

            # Execute with Claude
            response = await self.execute(
                prompt=prompt,
                max_tokens=2000,
                temperature=0.3  # Low temperature for consistent extraction
            )

            # Parse JSON response
            result_text = response.get("response", "{}")
            result = self._parse_json_response(result_text)

            # Validate and add defaults
            result = self._validate_and_fill_defaults(result, conversation_data)

            logger.info(f"Context Understanding complete: {len(result.get('people', []))} people, "
                       f"{len(result.get('topics_discussed', []))} topics")

            return result

        except Exception as e:
            logger.error(f"Context Understanding error: {e}")
            return self._get_minimal_response(conversation_data, str(e))

    def _parse_json_response(self, response_text: str) -> Dict[str, Any]:
        """
        Parse JSON from Claude response.

        Args:
            response_text: Response text from Claude

        Returns:
            Parsed JSON dict
        """
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

    def _validate_and_fill_defaults(
        self,
        result: Dict[str, Any],
        conversation_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Validate result and fill in defaults for missing fields.

        Args:
            result: Parsed result dict
            conversation_data: Original conversation data

        Returns:
            Validated result with defaults
        """
        # Required fields with defaults
        defaults = {
            "people": [],
            "companies_mentioned": [],
            "topics_discussed": [],
            "technologies_mentioned": [],
            "action_items": [],
            "key_interests": [],
            "pain_points_mentioned": [],
            "conversation_summary": "Conversation analyzed",
            "sentiment": "neutral",
            "goal_alignment": {
                "matches_user_goals": False,
                "which_goals": [],
                "alignment_score": 0.0
            }
        }

        # Fill in missing fields
        for key, default_value in defaults.items():
            if key not in result:
                result[key] = default_value

        # Validate people structure
        for person in result.get("people", []):
            if "speaker_id" not in person:
                person["speaker_id"] = "Unknown"
            for field in ["name", "role", "company", "email", "linkedin"]:
                if field not in person:
                    person[field] = None

        # Validate action items structure
        for item in result.get("action_items", []):
            if "assigned_to" not in item:
                item["assigned_to"] = "user"
            if "action" not in item:
                item["action"] = "Follow up"
            if "deadline" not in item:
                item["deadline"] = None
            if "priority" not in item:
                item["priority"] = "medium"

        # Ensure goal_alignment has all fields
        if "goal_alignment" in result:
            ga = result["goal_alignment"]
            if "matches_user_goals" not in ga:
                ga["matches_user_goals"] = False
            if "which_goals" not in ga:
                ga["which_goals"] = []
            if "alignment_score" not in ga:
                ga["alignment_score"] = 0.0

        return result

    def _get_minimal_response(
        self,
        conversation_data: Dict[str, Any],
        error_message: str
    ) -> Dict[str, Any]:
        """
        Return minimal valid response on error.

        Args:
            conversation_data: Original conversation data
            error_message: Error message

        Returns:
            Minimal valid response structure
        """
        return {
            "people": [],
            "companies_mentioned": [],
            "topics_discussed": [],
            "technologies_mentioned": [],
            "action_items": [],
            "key_interests": [],
            "pain_points_mentioned": [],
            "conversation_summary": f"Failed to parse conversation: {error_message}",
            "sentiment": "neutral",
            "goal_alignment": {
                "matches_user_goals": False,
                "which_goals": [],
                "alignment_score": 0.0
            },
            "error": error_message
        }
