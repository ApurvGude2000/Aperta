"""
Follow-Up Agent - Generates personalized follow-up messages (LinkedIn/Email) for each person met.
Runs after Context Understanding Agent completes, once per person.
"""
from typing import Dict, Any, Optional
import json
import re
from .base import ClaudeBaseAgent
from utils.logger import setup_logger

logger = setup_logger(__name__)


class FollowUpAgent(ClaudeBaseAgent):
    """
    Follow-Up Agent - Generates personalized follow-up messages.

    Purpose: Generate 3 message variants (Professional, Friendly, Value-First) for each person.
    When Called: After Context Understanding Agent completes, once per person.
    Output: JSON with 3 message variants (50-80 words each).
    """

    def __init__(self):
        """Initialize Follow-Up Agent."""
        system_prompt = """You are a Follow-Up Message Generator for professional networking.

TASK: Generate 3 follow-up message variants for LinkedIn.

OUTPUT FORMAT (JSON ONLY):
{
  "variants": [
    {
      "style": "Professional",
      "subject": "Subject line for LinkedIn connection request",
      "message": "Message body (50-80 words)"
    },
    {
      "style": "Friendly",
      "subject": "Subject line",
      "message": "Message body (50-80 words)"
    },
    {
      "style": "Value-First",
      "subject": "Subject line",
      "message": "Message body (50-80 words)"
    }
  ]
}

MESSAGE REQUIREMENTS:
1. Length: 50-80 words per message
2. Reference 1-2 specific conversation details
3. Include clear call-to-action (CTA)
4. Mention action items if applicable
5. No generic pleasantries ("Hope this finds you well")
6. Professional but warm tone
7. Make it personal and memorable

STYLE DEFINITIONS:
- Professional: Formal, business-focused, structured
- Friendly: Casual but professional, conversational
- Value-First: Lead with how you can help them

CONTEXT:
Person: {person_name}, {person_role} at {person_company}
Conversation Summary: {conversation_summary}
Topics Discussed: {topics_discussed}
Action Items: {action_items}
Key Interests: {key_interests}
Your Info: {user_name}, {user_role} at {user_company}
Event: {event_name}

JSON OUTPUT:"""

        super().__init__(
            name="follow_up",
            description="Generates personalized follow-up messages for networking contacts",
            system_prompt=system_prompt,
            priority=4
        )

        logger.info("Follow-Up Agent initialized")

    async def generate_messages(
        self,
        person_data: Dict[str, Any],
        context_data: Dict[str, Any],
        user_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate 3 follow-up message variants.

        Args:
            person_data: Dict with person info (name, role, company)
            context_data: Dict with conversation summary, topics, action items, interests
            user_context: Dict with user info (name, role, company, event)

        Returns:
            Dict with 3 message variants
        """
        try:
            logger.info(f"Generating follow-up messages for {person_data.get('name', 'Unknown')}")

            # Build prompt
            prompt = self._build_prompt(person_data, context_data, user_context)

            # Execute with Claude
            response = await self.execute(
                prompt=prompt,
                max_tokens=1500,
                temperature=0.7  # Creative but consistent
            )

            # Parse JSON response
            result_text = response.get("response", "{}")
            result = self._parse_json_response(result_text)

            # Validate and clean
            result = self._validate_messages(result)

            logger.info(f"Generated {len(result.get('variants', []))} message variants")

            return result

        except Exception as e:
            logger.error(f"Follow-up generation error: {e}")
            return self._get_fallback_messages(person_data, user_context)

    def _build_prompt(
        self,
        person_data: Dict[str, Any],
        context_data: Dict[str, Any],
        user_context: Dict[str, Any]
    ) -> str:
        """Build prompt with all context."""
        # Extract data with defaults
        person_name = person_data.get('name', 'Unknown')
        person_role = person_data.get('role', 'Professional')
        person_company = person_data.get('company', 'their company')

        conversation_summary = context_data.get('conversation_summary', 'Had a great conversation')
        topics_discussed = ', '.join(context_data.get('topics_discussed', []))
        key_interests = ', '.join(context_data.get('key_interests', []))

        # Format action items
        action_items = context_data.get('action_items', [])
        action_items_text = json.dumps(action_items) if action_items else "None"

        user_name = user_context.get('name', 'User')
        user_role = user_context.get('role', 'Professional')
        user_company = user_context.get('company', 'Company')
        event_name = user_context.get('event', 'the networking event')

        prompt = f"""Generate 3 personalized follow-up message variants.

PERSON: {person_name}, {person_role} at {person_company}
YOUR INFO: {user_name}, {user_role} at {user_company}
EVENT: {event_name}

CONVERSATION SUMMARY:
{conversation_summary}

TOPICS DISCUSSED:
{topics_discussed}

KEY INTERESTS:
{key_interests}

ACTION ITEMS:
{action_items_text}

Generate 3 message variants (Professional, Friendly, Value-First) as JSON."""

        return prompt

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

    def _validate_messages(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and clean message variants."""
        if "variants" not in result:
            result["variants"] = []

        # Ensure we have 3 variants
        expected_styles = ["Professional", "Friendly", "Value-First"]

        for variant in result["variants"]:
            # Check word count
            if "message" in variant:
                word_count = len(variant["message"].split())
                if word_count > 100:
                    logger.warning(f"Message too long: {word_count} words, truncating")
                    # Truncate to ~80 words
                    words = variant["message"].split()[:80]
                    variant["message"] = " ".join(words)

            # Ensure required fields
            if "style" not in variant:
                variant["style"] = "Professional"
            if "subject" not in variant:
                variant["subject"] = "Following up"
            if "message" not in variant:
                variant["message"] = "Looking forward to staying in touch."

        # If we don't have 3 variants, fill with defaults
        while len(result["variants"]) < 3:
            result["variants"].append({
                "style": expected_styles[len(result["variants"])],
                "subject": "Following up",
                "message": "Great meeting you! Let's stay in touch."
            })

        return result

    def _get_fallback_messages(
        self,
        person_data: Dict[str, Any],
        user_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Return fallback messages on error."""
        person_name = person_data.get('name', 'there')
        event_name = user_context.get('event', 'the event')

        return {
            "variants": [
                {
                    "style": "Professional",
                    "subject": f"Following up - {event_name}",
                    "message": f"Hi {person_name}, it was great meeting you at {event_name}. I enjoyed our conversation and would love to stay connected. Looking forward to keeping in touch."
                },
                {
                    "style": "Friendly",
                    "subject": f"Great meeting you at {event_name}!",
                    "message": f"Hey {person_name}! Really enjoyed chatting with you at {event_name}. Would love to stay in touch and continue our conversation. Let's connect!"
                },
                {
                    "style": "Value-First",
                    "subject": f"Resources from {event_name}",
                    "message": f"Hi {person_name}, following up from {event_name}. I have some resources that might be helpful based on our discussion. Happy to share and continue the conversation."
                }
            ],
            "error": "Used fallback messages due to generation error"
        }
