# ABOUTME: Q&A API endpoints for asking questions about conversations and managing Q&A sessions.
# ABOUTME: Routes questions to appropriate agents and stores interactions in the database.

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import List, Dict, Optional, Any
from datetime import datetime
import time

from db.session import get_db_session
from db.models import QASession, QAInteraction, Conversation
from agents.qa_orchestrator import QAOrchestrator
from agents.orchestrator import AgentOrchestrator
from services.rag_context import RAGContextManager
from utils.logger import setup_logger

logger = setup_logger(__name__)
router = APIRouter(prefix="/qa", tags=["Q&A"])


# Pydantic models for request/response
class AskQuestionRequest(BaseModel):
    question: str
    conversation_id: Optional[str] = None
    use_rag: bool = True
    user_id: str = "default_user"


class AskQuestionResponse(BaseModel):
    session_id: str
    interaction_id: str
    question: str
    final_answer: str
    routed_agents: List[str]
    execution_time: float
    timestamp: datetime
    agent_trace: Optional[Dict[str, Any]] = None


class QASessionSummary(BaseModel):
    id: str
    conversation_id: Optional[str]
    created_at: datetime
    interaction_count: int


class QAInteractionDetail(BaseModel):
    id: str
    question: str
    final_answer: Optional[str]
    routed_agents: List[str]
    responses: Dict[str, Any]
    execution_time: Optional[float]
    timestamp: datetime


class QASessionDetail(BaseModel):
    id: str
    conversation_id: Optional[str]
    created_at: datetime
    interactions: List[QAInteractionDetail]


# Initialize components (will be set during app startup)
qa_orchestrator_instance: Optional[QAOrchestrator] = None
orchestrator_instance: Optional[AgentOrchestrator] = None
rag_manager: Optional[RAGContextManager] = None


def set_qa_components(
    qa_orch: QAOrchestrator,
    orchestrator: AgentOrchestrator,
    rag: RAGContextManager
):
    """Set the Q&A orchestrator, orchestrator, and RAG manager instances."""
    global qa_orchestrator_instance, orchestrator_instance, rag_manager
    qa_orchestrator_instance = qa_orch
    orchestrator_instance = orchestrator
    rag_manager = rag


@router.post("/ask", response_model=AskQuestionResponse)
async def ask_question(
    request: AskQuestionRequest,
    db: AsyncSession = Depends(get_db_session)
) -> AskQuestionResponse:
    """
    Ask a question and route it to appropriate agents.
    
    Args:
        request: Question request with optional conversation context
        db: Database session
        
    Returns:
        Question answer with routing information
    """
    if not qa_orchestrator_instance:
        raise HTTPException(
            status_code=500,
            detail="Q&A orchestrator not initialized. Please check server startup."
        )

    start_time = time.time()

    try:
        # Get or create QA session
        session = QASession(
            conversation_id=request.conversation_id,
            user_id=request.user_id
        )
        db.add(session)
        await db.flush()

        # Use the new QA orchestrator to answer the question
        logger.info(f"Processing question: {request.question}")
        result = await qa_orchestrator_instance.answer_question(
            user_question=request.question,
            user_id=request.user_id
        )

        # Extract results
        final_answer = result.get("answer", "Unable to process your question.")
        agent_trace = result.get("agent_trace", {})
        execution_time = result.get("execution_time_ms", 0) / 1000.0  # Convert to seconds

        # Get routed agents from trace
        routing_info = agent_trace.get("routing", {})
        routed_agents = routing_info.get("agents_needed", [])

        # Get agent responses from trace
        agent_results = agent_trace.get("agent_results", {})

        # Store interaction
        interaction = QAInteraction(
            session_id=session.id,
            question=request.question,
            routed_agents=routed_agents,
            responses=agent_results,
            final_answer=final_answer,
            execution_time=execution_time
        )
        db.add(interaction)
        await db.commit()

        return AskQuestionResponse(
            session_id=session.id,
            interaction_id=interaction.id,
            question=request.question,
            final_answer=final_answer,
            routed_agents=routed_agents,
            execution_time=execution_time,
            timestamp=interaction.timestamp,
            agent_trace=agent_trace
        )
        
    except Exception as e:
        await db.rollback()
        logger.error(f"Error processing question: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing question: {str(e)}")


@router.get("/sessions", response_model=List[QASessionSummary])
async def list_sessions(
    db: AsyncSession = Depends(get_db_session),
    limit: int = 50,
    offset: int = 0
) -> List[QASessionSummary]:
    """
    List all Q&A sessions.
    
    Args:
        db: Database session
        limit: Maximum number of sessions to return
        offset: Number of sessions to skip
        
    Returns:
        List of Q&A session summaries
    """
    try:
        result = await db.execute(
            select(QASession)
            .order_by(QASession.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        sessions = result.scalars().all()
        
        summaries = []
        for session in sessions:
            # Count interactions
            interaction_result = await db.execute(
                select(QAInteraction).where(QAInteraction.session_id == session.id)
            )
            interactions = interaction_result.scalars().all()
            
            summaries.append(QASessionSummary(
                id=session.id,
                conversation_id=session.conversation_id,
                created_at=session.created_at,
                interaction_count=len(interactions)
            ))
        
        return summaries
        
    except Exception as e:
        logger.error(f"Error listing sessions: {e}")
        raise HTTPException(status_code=500, detail=f"Error listing sessions: {str(e)}")


@router.get("/sessions/{session_id}", response_model=QASessionDetail)
async def get_session(
    session_id: str,
    db: AsyncSession = Depends(get_db_session)
) -> QASessionDetail:
    """
    Get a specific Q&A session with all interactions.
    
    Args:
        session_id: Session ID
        db: Database session
        
    Returns:
        Q&A session detail with interactions
    """
    try:
        result = await db.execute(
            select(QASession).where(QASession.id == session_id)
        )
        session = result.scalar_one_or_none()
        
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Get all interactions
        interaction_result = await db.execute(
            select(QAInteraction)
            .where(QAInteraction.session_id == session_id)
            .order_by(QAInteraction.timestamp.asc())
        )
        interactions = interaction_result.scalars().all()
        
        return QASessionDetail(
            id=session.id,
            conversation_id=session.conversation_id,
            created_at=session.created_at,
            interactions=[
                QAInteractionDetail(
                    id=i.id,
                    question=i.question,
                    final_answer=i.final_answer,
                    routed_agents=i.routed_agents,
                    responses=i.responses,
                    execution_time=i.execution_time,
                    timestamp=i.timestamp
                )
                for i in interactions
            ]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting session: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting session: {str(e)}")


@router.post("/sessions/{session_id}/export")
async def export_session(
    session_id: str,
    format: str = "json",
    db: AsyncSession = Depends(get_db_session)
) -> Dict[str, Any]:
    """
    Export a Q&A session in JSON or CSV format.
    
    Args:
        session_id: Session ID
        format: Export format (json or csv)
        db: Database session
        
    Returns:
        Exported session data
    """
    if format not in ["json", "csv"]:
        raise HTTPException(status_code=400, detail="Format must be 'json' or 'csv'")
    
    try:
        # Get session detail
        session_detail = await get_session(session_id, db)
        
        if format == "json":
            return session_detail.model_dump()
        else:
            # CSV format - flatten interactions
            csv_data = []
            for interaction in session_detail.interactions:
                csv_data.append({
                    "session_id": session_detail.id,
                    "interaction_id": interaction.id,
                    "timestamp": interaction.timestamp.isoformat(),
                    "question": interaction.question,
                    "final_answer": interaction.final_answer,
                    "routed_agents": ", ".join(interaction.routed_agents),
                    "execution_time": interaction.execution_time
                })
            
            return {
                "format": "csv",
                "data": csv_data
            }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error exporting session: {e}")
        raise HTTPException(status_code=500, detail=f"Error exporting session: {str(e)}")


def _synthesize_answer(agent_results: List[Dict[str, Any]]) -> str:
    """
    Synthesize a final answer from multiple agent responses.
    
    Args:
        agent_results: List of agent results
        
    Returns:
        Synthesized answer string
    """
    if not agent_results:
        return "No agents were able to process your question."
    
    # Simple synthesis: concatenate non-empty results
    answers = []
    for result in agent_results:
        agent_name = result.get("agent_name") or result.get("agent", "Unknown")
        response = result.get("response", "")

        if response and isinstance(response, str) and response.strip():
            answers.append(f"**{agent_name}:**\n{response.strip()}")
    
    if not answers:
        return "The agents were unable to provide a meaningful answer."
    
    return "\n\n".join(answers)
