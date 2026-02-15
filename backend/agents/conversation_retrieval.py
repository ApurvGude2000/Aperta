"""
Conversation Retrieval Agent - Claude-powered agent that finds relevant conversations
and extracts key information from them to answer user questions.
"""
from typing import Dict, Any, List, Optional
import json
from .base import ClaudeBaseAgent
from utils.logger import setup_logger

logger = setup_logger(__name__)


class ConversationRetrievalAgent(ClaudeBaseAgent):
    """
    Conversation Retrieval Agent - Finds and extracts relevant conversation data.

    Purpose: Given conversation data as context, find relevant excerpts and
             extract key information to answer the user's question.
    When Called: As determined by Query Router, for Q&A system.
    Implementation: Claude-powered reasoning over conversation data passed as context.
    """

    def __init__(self):
        """Initialize Conversation Retrieval Agent."""
        system_prompt = """You are a Conversation Retrieval Agent. Your job is to search through conversation data and find relevant information to answer the user's question.

TASK: Given conversation data, find and extract the most relevant excerpts, quotes, and facts.

OUTPUT FORMAT (JSON ONLY):
{
  "results": [
    {
      "conversation_title": "Title of the conversation",
      "relevant_excerpt": "The most relevant part of the conversation (direct quote or summary)",
      "people_mentioned": ["Person 1", "Person 2"],
      "topics": ["Topic 1", "Topic 2"],
      "relevance": "Why this is relevant to the question (1 sentence)"
    }
  ],
  "total_found": 2,
  "summary": "Brief summary of what was found (1-2 sentences)"
}

RULES:
- Only include conversations that are actually relevant to the question
- Quote directly from transcripts when possible
- If no relevant conversations found, return empty results with total_found: 0
- Be precise - don't make up information not in the data
- Extract specific names, dates, action items, and topics when relevant

CONVERSATION DATA:
{conversation_data}

USER QUESTION: {user_question}

JSON OUTPUT:"""

        super().__init__(
            name="conversation_retrieval",
            description="Finds and extracts relevant conversation data to answer questions",
            system_prompt=system_prompt,
            priority=3
        )

        logger.info("Conversation Retrieval Agent initialized")

    async def execute(
        self,
        user_question: str,
        user_id: str,
        conversation_data: Optional[List[Dict[str, Any]]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Search through conversation data and extract relevant information.

        Args:
            user_question: User's search query
            user_id: User identifier
            conversation_data: List of conversation dicts with transcripts/summaries
                              (passed in by the orchestrator from the DB)

        Returns:
            Dict with search results
        """
        try:
            print(f"\n    [CONV_RETRIEVAL] Searching for: '{user_question}'")
            print(f"    [CONV_RETRIEVAL] user_id: {user_id}")
            print(f"    [CONV_RETRIEVAL] Conversation data provided: {conversation_data is not None}")
            if conversation_data:
                print(f"    [CONV_RETRIEVAL] Number of conversations: {len(conversation_data)}")
            logger.info(f"Searching conversations for: {user_question}")

            # If no conversation data provided, return empty
            if not conversation_data:
                print(f"    [CONV_RETRIEVAL] No conversation data provided, returning empty results")
                return {
                    "results": [],
                    "total_found": 0,
                    "query": user_question,
                    "summary": "No conversation data available to search."
                }

            # Build conversation context for Claude
            conversation_context = self._format_conversations(conversation_data)
            print(f"    [CONV_RETRIEVAL] Formatted context length: {len(conversation_context)} chars")

            # Build prompt
            prompt = f"""Search through these conversations and find information relevant to the question.

CONVERSATION DATA:
{conversation_context}

USER QUESTION: {user_question}

Find relevant excerpts, quotes, and facts. Return as JSON."""

            # Execute with Claude
            print(f"    [CONV_RETRIEVAL] Calling Claude API (model: {self.model})...")
            response = await super().execute(
                prompt=prompt,
                max_tokens=1500,
                temperature=0.3
            )
            print(f"    [CONV_RETRIEVAL] Claude response status: {response.get('status', 'unknown')}")

            # Parse JSON response
            result_text = response.get("response", "{}")
            print(f"    [CONV_RETRIEVAL] Raw response: {result_text[:200]}")
            parsed = self._parse_json_response(result_text)

            # Validate structure
            parsed = self._validate_results(parsed)

            print(f"    [CONV_RETRIEVAL] Found {parsed.get('total_found', 0)} relevant results")
            logger.info(f"Found {parsed.get('total_found', 0)} relevant results")

            return parsed

        except Exception as e:
            print(f"    [CONV_RETRIEVAL] ERROR: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            logger.error(f"Conversation retrieval error: {e}")
            return {
                "results": [],
                "total_found": 0,
                "query": user_question,
                "error": str(e)
            }

    def _format_conversations(self, conversations: List[Dict[str, Any]]) -> str:
        """Format conversation data into a readable context string for Claude."""
        formatted_parts = []

        for i, conv in enumerate(conversations, 1):
            title = conv.get("title", f"Conversation {i}")
            transcript = conv.get("transcript", "")
            event_name = conv.get("event_name", "")
            created_at = conv.get("created_at", "")

            # Build participants info
            participants = conv.get("participants", [])
            people_str = ""
            if participants:
                people_names = [
                    f"{p.get('name', 'Unknown')} ({p.get('company', '')})"
                    for p in participants if p.get("name")
                ]
                people_str = f"\nParticipants: {', '.join(people_names)}"

            # Build entities info
            entities = conv.get("entities", [])
            topics = [e.get("entity_value", "") for e in entities if e.get("entity_type") == "topic"]
            topics_str = f"\nTopics: {', '.join(topics)}" if topics else ""

            # Build action items
            action_items = conv.get("action_items", [])
            actions_str = ""
            if action_items:
                actions = [a.get("description", "") for a in action_items]
                actions_str = f"\nAction Items: {'; '.join(actions)}"

            # Truncate long transcripts
            if transcript and len(transcript) > 3000:
                transcript = transcript[:3000] + "... [truncated]"

            part = f"""--- Conversation {i}: {title} ---
Event: {event_name or 'N/A'}
Date: {created_at or 'N/A'}{people_str}{topics_str}{actions_str}
Transcript:
{transcript or '[No transcript available]'}
"""
            formatted_parts.append(part)

        return "\n".join(formatted_parts)

    def _parse_json_response(self, response_text: str) -> Dict[str, Any]:
        """Parse JSON from Claude response."""
        import re
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

    def _validate_results(self, parsed: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and normalize the results structure."""
        if "results" not in parsed:
            parsed["results"] = []
        if "total_found" not in parsed:
            parsed["total_found"] = len(parsed["results"])
        if "summary" not in parsed:
            parsed["summary"] = ""
        return parsed
