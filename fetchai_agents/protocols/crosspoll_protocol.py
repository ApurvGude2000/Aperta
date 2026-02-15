# ABOUTME: Protocol for cross-pollination agent communication.
# ABOUTME: Defines request/response schemas for suggesting strategic introductions.

from uagents import Model
from typing import List, Dict, Optional


class CrossPollinationRequest(Model):
    """Request to suggest introductions between people met at an event."""

    event_id: Optional[str] = None
    conversation_ids: Optional[List[str]] = None
    people_met: List[Dict]  # [{name, company, role, interests, goals, etc.}]
    min_match_score: float = 0.7  # Minimum relevance score for suggestions


class CrossPollinationResponse(Model):
    """Response containing suggested introductions with reasoning."""

    introductions: List[Dict]  # [{person_a, person_b, reason, priority, match_score}]
    total_suggested: int
    research_sources: Optional[List[str]] = None  # URLs of Perplexity research
    execution_time: float
    success: bool
    error: Optional[str] = None
