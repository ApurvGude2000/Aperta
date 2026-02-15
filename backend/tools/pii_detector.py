"""
PII Detection Tool - Identifies personally identifiable information in text.
"""
import re
from typing import List, Dict, Any, Set
from dataclasses import dataclass
from enum import Enum


class PIIType(str, Enum):
    """Types of PII that can be detected."""
    EMAIL = "email"
    PHONE = "phone"
    SSN = "ssn"
    CREDIT_CARD = "credit_card"
    ADDRESS = "address"
    NAME = "name"
    URL = "url"
    IP_ADDRESS = "ip_address"


@dataclass
class PIIMatch:
    """Represents a detected PII instance."""
    pii_type: PIIType
    value: str
    start: int
    end: int
    confidence: float
    context: str  # Surrounding text


class PIIDetector:
    """Detects various types of PII in text using regex patterns."""

    def __init__(self):
        """Initialize PII detector with regex patterns."""
        # Email pattern
        self.email_pattern = re.compile(
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        )

        # Phone patterns (various formats)
        self.phone_patterns = [
            re.compile(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b'),  # 555-123-4567 or 5551234567
            re.compile(r'\(\d{3}\)\s*\d{3}[-.]?\d{4}'),    # (555) 123-4567
            re.compile(r'\+1[-.]?\d{3}[-.]?\d{3}[-.]?\d{4}'),  # +1-555-123-4567
        ]

        # SSN pattern
        self.ssn_pattern = re.compile(
            r'\b\d{3}-\d{2}-\d{4}\b'
        )

        # Credit card pattern (simple - matches 13-19 digits with optional separators)
        self.credit_card_pattern = re.compile(
            r'\b(?:\d{4}[-\s]?){3}\d{4}\b'
        )

        # URL pattern (including LinkedIn, etc.)
        self.url_pattern = re.compile(
            r'(?:http[s]?://)?(?:www\.)?'
            r'(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}'
            r'(?:/[a-zA-Z0-9\-._~:/?#\[\]@!$&\'()*+,;=]*)?'
        )

        # IP address pattern
        self.ip_pattern = re.compile(
            r'\b(?:\d{1,3}\.){3}\d{1,3}\b'
        )

        # Common name indicators (for context-based detection)
        self.name_indicators = [
            'my name is', 'i\'m', 'this is', 'call me',
            'from', 'with', 'meet', 'contact'
        ]

    def detect_all(self, text: str, context_window: int = 30) -> List[PIIMatch]:
        """
        Detect all PII in the given text.

        Args:
            text: Text to scan for PII
            context_window: Characters to include before/after match for context

        Returns:
            List of detected PII matches
        """
        matches = []

        # Detect emails
        matches.extend(self._detect_emails(text, context_window))

        # Detect phone numbers
        matches.extend(self._detect_phones(text, context_window))

        # Detect SSNs
        matches.extend(self._detect_ssn(text, context_window))

        # Detect credit cards
        matches.extend(self._detect_credit_cards(text, context_window))

        # Detect URLs (LinkedIn, etc.)
        matches.extend(self._detect_urls(text, context_window))

        # Detect IP addresses
        matches.extend(self._detect_ip_addresses(text, context_window))

        # Sort by position in text
        matches.sort(key=lambda m: m.start)

        return matches

    def _detect_emails(self, text: str, context_window: int) -> List[PIIMatch]:
        """Detect email addresses."""
        matches = []
        for match in self.email_pattern.finditer(text):
            matches.append(PIIMatch(
                pii_type=PIIType.EMAIL,
                value=match.group(),
                start=match.start(),
                end=match.end(),
                confidence=0.95,  # Email regex is very reliable
                context=self._get_context(text, match.start(), match.end(), context_window)
            ))
        return matches

    def _detect_phones(self, text: str, context_window: int) -> List[PIIMatch]:
        """Detect phone numbers."""
        matches = []
        seen_positions = set()

        for pattern in self.phone_patterns:
            for match in pattern.finditer(text):
                # Avoid duplicate detections
                if match.start() in seen_positions:
                    continue
                seen_positions.add(match.start())

                # Validate it looks like a real phone number
                digits = re.sub(r'[^\d]', '', match.group())
                if len(digits) == 10 or len(digits) == 11:
                    matches.append(PIIMatch(
                        pii_type=PIIType.PHONE,
                        value=match.group(),
                        start=match.start(),
                        end=match.end(),
                        confidence=0.85,
                        context=self._get_context(text, match.start(), match.end(), context_window)
                    ))

        return matches

    def _detect_ssn(self, text: str, context_window: int) -> List[PIIMatch]:
        """Detect Social Security Numbers."""
        matches = []
        for match in self.ssn_pattern.finditer(text):
            matches.append(PIIMatch(
                pii_type=PIIType.SSN,
                value=match.group(),
                start=match.start(),
                end=match.end(),
                confidence=0.90,
                context=self._get_context(text, match.start(), match.end(), context_window)
            ))
        return matches

    def _detect_credit_cards(self, text: str, context_window: int) -> List[PIIMatch]:
        """Detect credit card numbers."""
        matches = []
        for match in self.credit_card_pattern.finditer(text):
            # Validate with Luhn algorithm check (optional enhancement)
            matches.append(PIIMatch(
                pii_type=PIIType.CREDIT_CARD,
                value=match.group(),
                start=match.start(),
                end=match.end(),
                confidence=0.75,  # Lower confidence without Luhn validation
                context=self._get_context(text, match.start(), match.end(), context_window)
            ))
        return matches

    def _detect_urls(self, text: str, context_window: int) -> List[PIIMatch]:
        """Detect URLs (including LinkedIn profiles)."""
        matches = []
        for match in self.url_pattern.finditer(text):
            url = match.group()
            # Only flag URLs that might contain PII (social media, personal sites)
            if any(site in url.lower() for site in ['linkedin', 'facebook', 'twitter', 'instagram']):
                matches.append(PIIMatch(
                    pii_type=PIIType.URL,
                    value=url,
                    start=match.start(),
                    end=match.end(),
                    confidence=0.80,
                    context=self._get_context(text, match.start(), match.end(), context_window)
                ))
        return matches

    def _detect_ip_addresses(self, text: str, context_window: int) -> List[PIIMatch]:
        """Detect IP addresses."""
        matches = []
        for match in self.ip_pattern.finditer(text):
            # Validate IP address octets are in range
            octets = match.group().split('.')
            if all(0 <= int(octet) <= 255 for octet in octets):
                matches.append(PIIMatch(
                    pii_type=PIIType.IP_ADDRESS,
                    value=match.group(),
                    start=match.start(),
                    end=match.end(),
                    confidence=0.70,
                    context=self._get_context(text, match.start(), match.end(), context_window)
                ))
        return matches

    def _get_context(self, text: str, start: int, end: int, window: int) -> str:
        """Extract context around a match."""
        context_start = max(0, start - window)
        context_end = min(len(text), end + window)
        context = text[context_start:context_end]

        # Add ellipsis if truncated
        if context_start > 0:
            context = '...' + context
        if context_end < len(text):
            context = context + '...'

        return context

    def get_statistics(self, matches: List[PIIMatch]) -> Dict[str, Any]:
        """Get statistics about detected PII."""
        stats = {
            'total_matches': len(matches),
            'by_type': {},
            'high_confidence': 0,
            'medium_confidence': 0,
            'low_confidence': 0
        }

        for match in matches:
            # Count by type
            pii_type = match.pii_type.value
            stats['by_type'][pii_type] = stats['by_type'].get(pii_type, 0) + 1

            # Count by confidence
            if match.confidence >= 0.85:
                stats['high_confidence'] += 1
            elif match.confidence >= 0.70:
                stats['medium_confidence'] += 1
            else:
                stats['low_confidence'] += 1

        return stats

    def to_json(self, matches: List[PIIMatch]) -> List[Dict[str, Any]]:
        """Convert matches to JSON-serializable format."""
        return [
            {
                'type': match.pii_type.value,
                'value': match.value,
                'start': match.start,
                'end': match.end,
                'confidence': match.confidence,
                'context': match.context
            }
            for match in matches
        ]


# Convenience function
def detect_pii(text: str) -> List[Dict[str, Any]]:
    """
    Quick function to detect PII in text.

    Args:
        text: Text to scan

    Returns:
        List of detected PII as dictionaries
    """
    detector = PIIDetector()
    matches = detector.detect_all(text)
    return detector.to_json(matches)
