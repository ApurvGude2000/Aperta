# ABOUTME: Protocol for context understanding agent communication.
# ABOUTME: Defines request/response schemas for entity extraction and conversation analysis.

from uagents import Model
from typing import List, Dict, Optional


class ContextExtractionRequest(Model):
    """Request to extract context from a conversation transcript."""

    conversation_id: str
    transcript: Optional[str] = None  # Optional if conversation already exists
    speaker_labels: Optional[Dict[str, str]] = None  # speaker_id -> name mapping
    user_goals: Optional[List[str]] = None


class ContextExtractionResponse(Model):
    """Response containing extracted conversation context."""

    conversation_id: str
    people: List[Dict]  # [{name, company, role, linkedin, etc.}]
    companies: List[str]
    topics: List[str]
    action_items: List[Dict]  # [{description, owner, priority, etc.}]
    sentiment: str
    summary: str
    execution_time: float
    success: bool
    error: Optional[str] = None
