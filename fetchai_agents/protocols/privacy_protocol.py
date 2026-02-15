# ABOUTME: Protocol for privacy guardian agent communication.
# ABOUTME: Defines request/response schemas for PII redaction from transcripts.

from uagents import Model
from typing import Optional


class PrivacyRedactionRequest(Model):
    """Request to redact PII from a transcript."""

    transcript: str
    redact_names: bool = False
    redact_emails: bool = True
    redact_phones: bool = True
    redact_addresses: bool = True


class PrivacyRedactionResponse(Model):
    """Response containing redacted transcript and statistics."""

    redacted_text: str
    redactions_made: int
    redaction_types: dict  # {type: count} e.g., {"email": 2, "phone": 1}
    execution_time: float
    success: bool
    error: Optional[str] = None
