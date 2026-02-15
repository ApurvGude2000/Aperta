"""
Agent System - Multi-agent architecture for Aperta networking AI.

This module provides a comprehensive agent system for:
1. Data Capture: Privacy protection before database storage
2. Post-Event Processing: Context understanding, follow-ups, cross-pollination
3. Question-Answering: Query routing, retrieval, insights, recommendations

Architecture:
- Privacy Guardian: Redacts PII before database save
- Context Understanding: Extracts entities and insights from conversations
- Follow-Up: Generates personalized messages (3 variants)
- Cross-Pollination: Finds introduction opportunities with Perplexity research
- Query Router: Routes user questions to appropriate agents
- Conversation Retrieval: Searches conversations with vector similarity
- Insight: Analyzes patterns and trends
- Recommendation: Suggests next actions
- Response Composer: Synthesizes final answers

Orchestration:
- QAOrchestrator: Manages question-answering pipeline
- AgentOrchestrator: General-purpose agent coordination
"""

# Base classes
from .base import ClaudeBaseAgent

# Data Capture Phase Agents
from .privacy_guardian import PrivacyGuardianAgent, redact_pii

# Post-Event Processing Agents
from .context_understanding import ContextUnderstandingAgent
from .follow_up import FollowUpAgent
from .cross_pollination import CrossPollinationAgent

# Q&A System Agents
from .query_router import QueryRouterAgent
from .conversation_retrieval import ConversationRetrievalAgent
from .insight import InsightAgent
from .recommendation import RecommendationAgent
from .response_composer import ResponseComposerAgent

# Orchestration
from .orchestrator import AgentOrchestrator, orchestrator
from .qa_orchestrator import QAOrchestrator, qa_orchestrator

__all__ = [
    # Base
    "ClaudeBaseAgent",

    # Data Capture
    "PrivacyGuardianAgent",
    "redact_pii",

    # Post-Event Processing
    "ContextUnderstandingAgent",
    "FollowUpAgent",
    "CrossPollinationAgent",

    # Q&A System
    "QueryRouterAgent",
    "ConversationRetrievalAgent",
    "InsightAgent",
    "RecommendationAgent",
    "ResponseComposerAgent",

    # Orchestration
    "AgentOrchestrator",
    "orchestrator",
    "QAOrchestrator",
    "qa_orchestrator",
]

# Version info
__version__ = "2.0.0"
__author__ = "Aperta Team"
__description__ = "Multi-agent AI system for networking intelligence"
