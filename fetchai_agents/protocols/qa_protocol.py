# ABOUTME: Protocol for Q&A system agent communication.
# ABOUTME: Defines request/response schemas for question answering over conversation history.

from uagents import Model
from typing import List, Optional, Dict, Any


class QARequest(Model):
    """Request to answer a question about conversation history."""

    question: str
    user_id: Optional[str] = None
    conversation_id: Optional[str] = None  # Limit to specific conversation
    use_rag: bool = True  # Use semantic search over conversation history
    max_context_conversations: int = 5  # Max conversations to include in context


class QAResponse(Model):
    """Response containing the answer and agent execution trace."""

    question: str
    final_answer: str
    agents_used: List[str]  # List of agent names involved in answering
    source_conversations: Optional[List[str]] = None  # IDs of conversations referenced
    confidence_score: Optional[float] = None
    agent_trace: Optional[Dict[str, Any]] = None  # Detailed agent execution trace
    execution_time: float
    success: bool
    error: Optional[str] = None
