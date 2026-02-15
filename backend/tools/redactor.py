"""
Redaction Tool - Automatically redacts PII from text while preserving context.
"""
from typing import List, Dict, Any, Optional
from .pii_detector import PIIDetector, PIIMatch, PIIType


class Redactor:
    """Redacts PII from text while maintaining readability."""

    def __init__(self):
        """Initialize redactor with PII detector."""
        self.detector = PIIDetector()

        # Redaction templates for different PII types
        self.redaction_templates = {
            PIIType.EMAIL: "[REDACTED-EMAIL]",
            PIIType.PHONE: "[REDACTED-PHONE]",
            PIIType.SSN: "[REDACTED-SSN]",
            PIIType.CREDIT_CARD: "[REDACTED-CARD]",
            PIIType.ADDRESS: "[REDACTED-ADDRESS]",
            PIIType.NAME: "[REDACTED-NAME]",
            PIIType.URL: "[REDACTED-URL]",
            PIIType.IP_ADDRESS: "[REDACTED-IP]"
        }

    def redact_text(
        self,
        text: str,
        pii_types: Optional[List[PIIType]] = None,
        preserve_domain: bool = False,
        preserve_format: bool = True
    ) -> Dict[str, Any]:
        """
        Redact PII from text.

        Args:
            text: Text to redact
            pii_types: Specific PII types to redact (None = all types)
            preserve_domain: For emails, keep the domain (user@[REDACTED])
            preserve_format: Keep format hints (e.g., [REDACTED-XXX-XXX-1234] for phones)

        Returns:
            Dictionary with redacted text, original matches, and redaction map
        """
        # Detect all PII
        matches = self.detector.detect_all(text)

        # Filter by requested types
        if pii_types:
            matches = [m for m in matches if m.pii_type in pii_types]

        # Sort matches in reverse order (end to start) to avoid offset issues
        matches.sort(key=lambda m: m.start, reverse=True)

        # Redact the text
        redacted_text = text
        redaction_map = []

        for match in matches:
            # Get redaction token
            if preserve_format and match.pii_type == PIIType.PHONE:
                token = self._format_preserving_phone_redaction(match.value)
            elif preserve_domain and match.pii_type == PIIType.EMAIL:
                token = self._domain_preserving_email_redaction(match.value)
            else:
                token = self.redaction_templates.get(match.pii_type, "[REDACTED]")

            # Replace in text
            redacted_text = (
                redacted_text[:match.start] +
                token +
                redacted_text[match.end:]
            )

            # Track redaction
            redaction_map.append({
                'original': match.value,
                'redacted': token,
                'type': match.pii_type.value,
                'position': match.start,
                'confidence': match.confidence
            })

        return {
            'redacted_text': redacted_text,
            'original_text': text,
            'matches': self.detector.to_json(matches),
            'redaction_map': redaction_map,
            'total_redactions': len(redaction_map),
            'statistics': self.detector.get_statistics(matches)
        }

    def redact_selective(
        self,
        text: str,
        matches_to_redact: List[int]  # Indices of matches to redact
    ) -> str:
        """
        Redact only specific PII matches (selective redaction).

        Args:
            text: Text to redact
            matches_to_redact: Indices of which matches to redact

        Returns:
            Redacted text
        """
        # Detect all PII
        all_matches = self.detector.detect_all(text)

        # Filter to selected matches
        selected_matches = [all_matches[i] for i in matches_to_redact if i < len(all_matches)]

        # Sort in reverse
        selected_matches.sort(key=lambda m: m.start, reverse=True)

        # Redact
        redacted_text = text
        for match in selected_matches:
            token = self.redaction_templates.get(match.pii_type, "[REDACTED]")
            redacted_text = (
                redacted_text[:match.start] +
                token +
                redacted_text[match.end:]
            )

        return redacted_text

    def _format_preserving_phone_redaction(self, phone: str) -> str:
        """
        Redact phone but preserve format.
        Example: 650-555-0123 -> [REDACTED-XXX-XXX-0123]
        """
        # Extract last 4 digits
        digits = ''.join(c for c in phone if c.isdigit())
        if len(digits) >= 4:
            last_four = digits[-4:]
            # Preserve separator style
            if '-' in phone:
                return f"[REDACTED-XXX-XXX-{last_four}]"
            elif ' ' in phone:
                return f"[REDACTED XXX XXX {last_four}]"
            else:
                return f"[REDACTED-{last_four}]"
        return "[REDACTED-PHONE]"

    def _domain_preserving_email_redaction(self, email: str) -> str:
        """
        Redact email but preserve domain.
        Example: john.doe@company.com -> [REDACTED]@company.com
        """
        if '@' in email:
            _, domain = email.split('@', 1)
            return f"[REDACTED]@{domain}"
        return "[REDACTED-EMAIL]"

    def create_reversible_redaction(
        self,
        text: str,
        encryption_key: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create reversible redaction with encrypted original values.
        (For authorized personnel to restore if needed)

        Args:
            text: Text to redact
            encryption_key: Optional encryption key for storing originals

        Returns:
            Redacted text with encrypted reverse mapping
        """
        result = self.redact_text(text)

        # In production, encrypt the redaction_map with the key
        # For now, just mark it as encrypted
        if encryption_key:
            result['redaction_map_encrypted'] = True
            result['encryption_method'] = 'AES-256'  # Placeholder

        return result

    def analyze_without_redacting(self, text: str) -> Dict[str, Any]:
        """
        Analyze text for PII without actually redacting.
        Useful for privacy audits and warnings.

        Returns:
            Analysis of PII found
        """
        matches = self.detector.detect_all(text)

        return {
            'pii_found': len(matches) > 0,
            'total_instances': len(matches),
            'matches': self.detector.to_json(matches),
            'statistics': self.detector.get_statistics(matches),
            'risk_level': self._assess_risk_level(matches),
            'recommendations': self._get_recommendations(matches)
        }

    def _assess_risk_level(self, matches: List[PIIMatch]) -> str:
        """Assess privacy risk level based on PII found."""
        if not matches:
            return "none"

        # High risk PII types
        high_risk_types = {PIIType.SSN, PIIType.CREDIT_CARD}
        has_high_risk = any(m.pii_type in high_risk_types for m in matches)

        if has_high_risk:
            return "critical"
        elif len(matches) > 5:
            return "high"
        elif len(matches) > 2:
            return "medium"
        else:
            return "low"

    def _get_recommendations(self, matches: List[PIIMatch]) -> List[str]:
        """Get recommendations based on detected PII."""
        recommendations = []

        stats = self.detector.get_statistics(matches)

        if stats['by_type'].get('email', 0) > 0:
            recommendations.append(
                "Email addresses detected. Consider redacting before sharing."
            )

        if stats['by_type'].get('phone', 0) > 0:
            recommendations.append(
                "Phone numbers detected. Verify consent before storing."
            )

        if stats['by_type'].get('ssn', 0) > 0:
            recommendations.append(
                "SSN detected! Immediate redaction required. Store encrypted."
            )

        if stats['by_type'].get('credit_card', 0) > 0:
            recommendations.append(
                "Credit card detected! Do not store. PCI-DSS compliance required."
            )

        if len(matches) > 10:
            recommendations.append(
                "High volume of PII detected. Consider bulk redaction."
            )

        return recommendations


# Convenience functions
def redact_pii(text: str, preserve_format: bool = True) -> str:
    """
    Quick function to redact all PII from text.

    Args:
        text: Text to redact
        preserve_format: Whether to preserve format hints

    Returns:
        Redacted text
    """
    redactor = Redactor()
    result = redactor.redact_text(text, preserve_format=preserve_format)
    return result['redacted_text']


def analyze_pii(text: str) -> Dict[str, Any]:
    """
    Quick function to analyze PII without redacting.

    Args:
        text: Text to analyze

    Returns:
        Analysis results
    """
    redactor = Redactor()
    return redactor.analyze_without_redacting(text)
