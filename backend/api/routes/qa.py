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
from agents.intelligent_router import IntelligentRouter
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


class AskQuestionResponse(BaseModel):
    session_id: str
    interaction_id: str
    question: str
    final_answer: str
    routed_agents: List[str]
    execution_time: float
    timestamp: datetime


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
router_instance: Optional[IntelligentRouter] = None
orchestrator_instance: Optional[AgentOrchestrator] = None
rag_manager: Optional[RAGContextManager] = None


def set_qa_components(
    router: IntelligentRouter,
    orchestrator: AgentOrchestrator,
    rag: RAGContextManager
):
    """Set the router, orchestrator, and RAG manager instances."""
    global router_instance, orchestrator_instance, rag_manager
    router_instance = router
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
    if not router_instance or not orchestrator_instance:
        raise HTTPException(
            status_code=500,
            detail="Q&A components not initialized. Please check server startup."
        )
    
    start_time = time.time()
    
    try:
        # Get or create QA session
        # For now, create a new session for each question
        # In production, you might want to group related questions
        session = QASession(
            conversation_id=request.conversation_id,
            user_id="default_user"  # TODO: Get from auth context
        )
        db.add(session)
        await db.flush()
        
        # Load RAG context if requested and conversation exists
        context = ""
        if request.use_rag and request.conversation_id:
            logger.info(f"Loading context for conversation_id: {request.conversation_id}")
            try:
                # Get conversation transcript
                result = await db.execute(
                    select(Conversation).where(Conversation.id == request.conversation_id)
                )
                conversation = result.scalar_one_or_none()

                if conversation:
                    logger.info(f"Conversation found: {conversation.title}")
                    if conversation.transcript:
                        transcript_length = len(conversation.transcript)
                        logger.info(f"Transcript found, length: {transcript_length} chars")

                        # For now, always use full transcript
                        # RAG could be used to chunk and retrieve relevant parts for very long transcripts
                        context = conversation.transcript
                        logger.info(f"Using full transcript as context, length: {len(context)} chars")
                    else:
                        logger.warning(f"Conversation {request.conversation_id} has no transcript")
                else:
                    logger.warning(f"Conversation {request.conversation_id} not found")
            except Exception as e:
                logger.error(f"Failed to load RAG context: {e}", exc_info=True)
        else:
            if not request.use_rag:
                logger.info("RAG disabled by request")
            if not request.conversation_id:
                logger.info("No conversation_id provided, answering general question")
        
        # Build full query with context
        full_query = request.question
        if context:
            full_query = f"Context:\n{context}\n\nQuestion: {request.question}"
            logger.info(f"Built full_query with context, total length: {len(full_query)} chars")
        else:
            logger.info("No context available, using question only")
        
        # Route the question to appropriate agents
        routing_decision = await router_instance.route_query(
            query=full_query,
            context={"conversation_id": request.conversation_id} if request.conversation_id else None
        )
        
        # Build agent requests for orchestrator
        agent_requests = [
            {
                "agent_name": agent_name,
                "prompt": full_query,
                "context": {"conversation_id": request.conversation_id} if request.conversation_id else None
            }
            for agent_name in routing_decision.get("recommended_agents", [])
        ]

        # Log what we're sending to agents
        for req in agent_requests:
            logger.info(f"Agent request for {req['agent_name']}: prompt_length={len(req['prompt'])} chars")

        # Execute agents via orchestrator (parallel execution)
        if agent_requests:
            agent_results = await orchestrator_instance.execute_agents_parallel(agent_requests)
        else:
            # No agents selected, use a default response
            agent_results = []

        # Extract responses
        agent_responses = {}
        for agent_result in agent_results:
            agent_name = agent_result["agent_name"]
            agent_responses[agent_name] = agent_result.get("response", "")

        # Synthesize final answer from agent responses
        final_answer = _synthesize_answer(agent_results)
        
        execution_time = time.time() - start_time
        
        # Store interaction
        interaction = QAInteraction(
            session_id=session.id,
            question=request.question,
            routed_agents=routing_decision.get("recommended_agents", []),
            responses=agent_responses,
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
            routed_agents=routing_decision.get("recommended_agents", []),
            execution_time=execution_time,
            timestamp=interaction.timestamp
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
