"""
Cross-Pollination Agent - Finds introduction opportunities between people met.
Uses Perplexity API to enrich person data with research.
Runs after all Context Understanding Agents complete, once per event (if 3+ people).
"""
from typing import Dict, Any, List, Optional
import json
import re
import httpx
from .base import ClaudeBaseAgent
from utils.logger import setup_logger
from config import settings

logger = setup_logger(__name__)


class CrossPollinationAgent(ClaudeBaseAgent):
    """
    Cross-Pollination Agent - Finds introduction opportunities with Perplexity research.

    Purpose: Find connections between people met, enriched with Perplexity research.
    When Called: After all Context Understanding completes, once per event (if 3+ people).
    Output: JSON with introduction suggestions.
    """

    def __init__(self):
        """Initialize Cross-Pollination Agent."""
        system_prompt = """You are a Connection Finder Agent analyzing networking data to suggest introductions.

TASK: Find introduction opportunities where Person A and Person B should meet.

OUTPUT FORMAT (JSON ONLY):
{
  "introductions": [
    {
      "person_a": "Full name",
      "person_b": "Full name",
      "reason": "Why they should meet (max 25 words)",
      "mutual_benefit": "What both gain (max 20 words)",
      "priority": "high" or "medium" or "low",
      "suggested_context": "How to frame the intro (max 30 words)"
    }
  ]
}

MATCHING CRITERIA:
1. Person A's needs match Person B's skills (or vice versa)
2. Overlapping interests/topics
3. Complementary roles (investor + founder, engineer + hiring manager)
4. Geographic or industry connections
5. Clear mutual benefit (not one-sided)

PRIORITY LEVELS:
- high: Both parties explicitly mentioned relevant need/skill
- medium: Strong overlap but implicit need
- low: Weak connection, speculative

RULES:
1. Max 5 introduction suggestions
2. Only suggest if CLEAR mutual benefit
3. Avoid suggesting competitors in same space
4. Consider: Would you personally make this intro?
5. Use Perplexity research to validate connections

PEOPLE DATA:
{people_data_json}

JSON OUTPUT:"""

        super().__init__(
            name="cross_pollination",
            description="Finds introduction opportunities between people met",
            system_prompt=system_prompt,
            priority=5
        )

        self.perplexity_api_key = settings.perplexity_api_key
        logger.info("Cross-Pollination Agent initialized")

    async def find_connections(
        self,
        people_met: List[Dict[str, Any]],
        event_id: str
    ) -> Dict[str, Any]:
        """
        Find introduction opportunities with Perplexity enrichment.

        Args:
            people_met: List of people data from Context Understanding
                Each person should have: name, role, company, interests, needs, skills
            event_id: Event identifier

        Returns:
            Dict with introduction suggestions
        """
        try:
            logger.info(f"Finding connections for {len(people_met)} people from event {event_id}")

            if len(people_met) < 2:
                logger.info("Not enough people for cross-pollination")
                return {"introductions": [], "reason": "Need at least 2 people"}

            # Step 1: Enrich each person with Perplexity research
            enriched_people = []
            for person in people_met:
                try:
                    enriched = await self._enrich_with_perplexity(person)
                    enriched_people.append(enriched)
                except Exception as e:
                    logger.error(f"Perplexity enrichment failed for {person.get('name')}: {e}")
                    enriched_people.append(person)  # Use original data

            # Step 2: Find connections using Claude
            connections = await self._find_connections_with_claude(enriched_people)

            logger.info(f"Found {len(connections.get('introductions', []))} introduction opportunities")

            return connections

        except Exception as e:
            logger.error(f"Cross-pollination error: {e}")
            return {"introductions": [], "error": str(e)}

    async def _enrich_with_perplexity(self, person: Dict[str, Any]) -> Dict[str, Any]:
        """
        Use Perplexity Sonar API to research person and enrich context.

        Args:
            person: Person data dict

        Returns:
            Enriched person data with perplexity_research field
        """
        if not self.perplexity_api_key:
            logger.warning("Perplexity API key not configured, skipping enrichment")
            person["perplexity_research"] = "No API key configured"
            return person

        name = person.get('name', '')
        role = person.get('role', '')
        company = person.get('company', '')

        if not name:
            person["perplexity_research"] = "No name provided"
            return person

        # Build search query
        query = f"{name}"
        if role:
            query += f" {role}"
        if company:
            query += f" at {company}"

        logger.info(f"Researching: {query}")

        try:
            # Call Perplexity Sonar API
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.perplexity.ai/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.perplexity_api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "sonar",
                        "messages": [
                            {
                                "role": "user",
                                "content": f"Who is {query}? Provide a brief professional summary in 2-3 sentences."
                            }
                        ],
                        "max_tokens": 200,
                        "temperature": 0.2,
                        "search_recency_filter": "month"  # Recent info
                    },
                    timeout=30.0
                )

            if response.status_code == 200:
                data = response.json()
                research = data.get("choices", [{}])[0].get("message", {}).get("content", "")
                person["perplexity_research"] = research
                logger.info(f"Perplexity research complete for {name}")
            else:
                logger.warning(f"Perplexity API error: {response.status_code}")
                person["perplexity_research"] = f"API error: {response.status_code}"

        except Exception as e:
            logger.error(f"Perplexity API call failed: {e}")
            person["perplexity_research"] = f"Research failed: {str(e)}"

        return person

    async def _find_connections_with_claude(
        self,
        enriched_people: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Use Claude to find connection opportunities.

        Args:
            enriched_people: List of people with Perplexity research

        Returns:
            Dict with introduction suggestions
        """
        # Build prompt with enriched data
        people_json = json.dumps(enriched_people, indent=2)

        prompt = f"""Analyze these people and find introduction opportunities.

Each person has been enriched with recent professional research from Perplexity.

PEOPLE MET:
{people_json}

Find connections and return JSON with introduction suggestions."""

        try:
            # Execute with Claude
            response = await self.execute(
                prompt=prompt,
                max_tokens=2000,
                temperature=0.4  # Balanced creativity and consistency
            )

            # Parse JSON response
            result_text = response.get("response", "{}")
            result = self._parse_json_response(result_text)

            # Validate
            result = self._validate_connections(result)

            return result

        except Exception as e:
            logger.error(f"Claude connection finding error: {e}")
            return {"introductions": [], "error": str(e)}

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

    def _validate_connections(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Validate introduction suggestions."""
        if "introductions" not in result:
            result["introductions"] = []

        # Limit to 5 introductions
        result["introductions"] = result["introductions"][:5]

        # Validate each introduction
        for intro in result["introductions"]:
            # Ensure required fields
            if "person_a" not in intro:
                intro["person_a"] = "Unknown"
            if "person_b" not in intro:
                intro["person_b"] = "Unknown"
            if "reason" not in intro:
                intro["reason"] = "Potential connection"
            if "mutual_benefit" not in intro:
                intro["mutual_benefit"] = "Mutual benefit identified"
            if "priority" not in intro or intro["priority"] not in ["high", "medium", "low"]:
                intro["priority"] = "medium"
            if "suggested_context" not in intro:
                intro["suggested_context"] = "Consider introducing these contacts"

        return result
