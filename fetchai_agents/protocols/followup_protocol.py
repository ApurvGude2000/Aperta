# ABOUTME: Protocol for follow-up message generation agent.
# ABOUTME: Defines request/response schemas for creating personalized follow-up messages.

from uagents import Model
from typing import List, Dict, Optional


class FollowUpRequest(Model):
    """Request to generate follow-up messages for a person met."""

    person_name: str
    person_company: Optional[str] = None
    person_role: Optional[str] = None
    conversation_context: str
    conversation_id: Optional[str] = None
    tone_preferences: Optional[List[str]] = None  # ["professional", "casual", "enthusiastic"]


class FollowUpResponse(Model):
    """Response containing generated follow-up message variants."""

    person_name: str
    variants: List[Dict]  # [{style: str, subject: str, message: str}]
    generated_at: str
    execution_time: float
    success: bool
    error: Optional[str] = None
