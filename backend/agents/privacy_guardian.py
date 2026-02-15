"""
Privacy Guardian Agent - Detects and redacts PII from transcripts before database storage.
Runs on every transcript chunk (every 3 seconds during recording).
"""
from typing import Optional
import re
import json
from .base import ClaudeBaseAgent
from utils.logger import setup_logger

logger = setup_logger(__name__)


class PrivacyGuardianAgent(ClaudeBaseAgent):
    """
    Privacy Guardian Agent - Redacts PII before database save.

    Purpose: Detect and redact PII from text.
    When Called: Every transcript chunk (every 3 seconds during recording).
    Output: Plain text with PII redacted (NO JSON, NO markdown).
    """

    def __init__(self):
        """Initialize Privacy Guardian Agent."""
        system_prompt = """You are a Privacy Guardian Agent. Your job is to detect and redact PII (Personally Identifiable Information) from text.

REDACTION RULES:
1. Phone numbers → [PHONE]
2. Email addresses → [EMAIL]
3. SSN (XXX-XX-XXXX) → [SSN]
4. Credit card numbers → [CREDIT_CARD]
5. Street addresses → [ADDRESS]
6. Keep: Names, companies, job titles (these are networking data)

OUTPUT REQUIREMENTS:
- Return ONLY the redacted text
- NO JSON, NO explanations, NO markdown
- NO preamble like "Here is the redacted text:"
- Preserve exact structure and punctuation
- If no PII found, return text unchanged

INPUT TEXT:
{transcript_text}

REDACTED TEXT:"""

        super().__init__(
            name="privacy_guardian",
            description="Protects privacy by detecting and redacting PII before database storage",
            system_prompt=system_prompt,
            priority=1  # Highest priority - runs before database save
        )

        logger.info("Privacy Guardian Agent initialized")

    async def redact_transcript(self, transcript_text: str) -> str:
        """
        Redact PII from transcript text.

        Args:
            transcript_text: Raw transcript text

        Returns:
            Redacted text with PII replaced by [PHONE], [EMAIL], etc.
        """
        if not transcript_text or not transcript_text.strip():
            return transcript_text

        try:
            logger.info(f"Privacy Guardian redacting text ({len(transcript_text)} chars)")

            # Build prompt
            prompt = transcript_text

            # Execute with Claude
            response = await self.execute(
                prompt=prompt,
                max_tokens=min(len(transcript_text) * 2, 4096),  # Allow for expansion
                temperature=0.0  # Deterministic
            )

            # Extract plain text response
            redacted = response.get("response", "").strip()

            # Clean response (remove any JSON, markdown, preamble)
            redacted = self._clean_response(redacted, transcript_text)

            # Validate output
            if self._is_output_valid(redacted, transcript_text):
                logger.info(f"Privacy Guardian completed: {len(redacted)} chars")
                return redacted
            else:
                logger.warning("Privacy Guardian output invalid, using original")
                return transcript_text

        except Exception as e:
            logger.error(f"Privacy Guardian error: {e}, using original text")
            return transcript_text

    def _clean_response(self, response: str, original: str) -> str:
        """
        Clean response to extract just the redacted text.

        Args:
            response: Claude's response
            original: Original text for fallback

        Returns:
            Cleaned text
        """
        # Remove markdown code blocks
        if response.startswith("```"):
            lines = response.split("\n")
            # Remove first and last lines if they're markdown fences
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            response = "\n".join(lines)

        # Remove JSON wrapping
        if response.startswith("{") and response.endswith("}"):
            try:
                data = json.loads(response)
                # Try to extract text from common JSON structures
                if "redacted_text" in data:
                    response = data["redacted_text"]
                elif "text" in data:
                    response = data["text"]
                elif "response" in data:
                    response = data["response"]
            except json.JSONDecodeError:
                pass

        # Remove common preambles
        preambles = [
            "Here is the redacted text:",
            "Redacted text:",
            "REDACTED TEXT:",
            "Here's the redacted text:",
            "The redacted text is:",
        ]
        for preamble in preambles:
            if response.lower().startswith(preamble.lower()):
                response = response[len(preamble):].strip()

        return response.strip()

    def _is_output_valid(self, redacted: str, original: str) -> bool:
        """
        Validate that output is reasonable.

        Args:
            redacted: Redacted text
            original: Original text

        Returns:
            True if valid, False otherwise
        """
        # Check if output exists
        if not redacted:
            return False

        # Check if length change is reasonable (within 50% of original)
        length_ratio = len(redacted) / max(len(original), 1)
        if length_ratio > 1.5 or length_ratio < 0.5:
            logger.warning(f"Output length changed too much: {length_ratio:.2f}x")
            return False

        return True


# Convenience function for quick redaction
async def redact_pii(text: str) -> str:
    """
    Quick function to redact PII from text.

    Args:
        text: Text to redact

    Returns:
        Redacted text
    """
    agent = PrivacyGuardianAgent()
    return await agent.redact_transcript(text)


# Allow running as script for testing
if __name__ == "__main__":
    import asyncio
    import sys

    # Fix imports when running as script
    sys.path.insert(0, '/Users/jedrzejcader/echopear/Aperta/backend')

    async def test():
        """Test the privacy guardian with sample text."""
        agent = PrivacyGuardianAgent()

        test_text = """
        My name is John Doe and you can reach me at john.doe@email.com or
        call me at 555-123-4567. I live at 123 Main Street, New York, NY.
        My SSN is 123-45-6789 and my credit card is 4532-1234-5678-9012.
        """

        print("Original text:")
        print(test_text)
        print("\n" + "="*60 + "\n")

        redacted = await agent.redact_transcript(test_text)

        print("Redacted text:")
        print(redacted)

    asyncio.run(test())
