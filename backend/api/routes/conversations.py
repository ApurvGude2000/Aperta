# ABOUTME: Conversation management API endpoints for CRUD operations.
# ABOUTME: Handles creation, retrieval, update, and deletion of conversation records.

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from sqlalchemy.orm import selectinload
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

from db.session import get_db_session
from db.models import Conversation, Participant, Entity, ActionItem
from agents.orchestrator import AgentOrchestrator
from services.transcript_storage import transcript_storage
from utils.logger import setup_logger

logger = setup_logger(__name__)
router = APIRouter(prefix="/conversations", tags=["Conversations"])


# Pydantic models for request/response
class ConversationCreate(BaseModel):
    title: Optional[str] = None
    transcript: str
    status: str = "active"
    recording_url: Optional[str] = None
    location: Optional[str] = None
    event_name: Optional[str] = None
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None


class ConversationUpdate(BaseModel):
    title: Optional[str] = None
    transcript: Optional[str] = None
    status: Optional[str] = None
    recording_url: Optional[str] = None
    location: Optional[str] = None
    event_name: Optional[str] = None
    ended_at: Optional[datetime] = None


class ParticipantResponse(BaseModel):
    id: str
    name: Optional[str]
    email: Optional[str]
    company: Optional[str]
    title: Optional[str]
    linkedin_url: Optional[str]
    phone: Optional[str]
    consent_status: str
    lead_priority: Optional[str]
    lead_score: float


class EntityResponse(BaseModel):
    id: str
    entity_type: str
    entity_value: str
    confidence: float
    context: Optional[str]


class ActionItemResponse(BaseModel):
    id: str
    description: str
    responsible_party: Optional[str]
    due_date: Optional[datetime]
    completed: bool


class ConversationResponse(BaseModel):
    id: str
    user_id: str
    title: Optional[str]
    status: str
    transcript: Optional[str]
    recording_url: Optional[str]
    location: Optional[str]
    event_name: Optional[str]
    started_at: datetime
    ended_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    participants: List[ParticipantResponse] = []
    entities: List[EntityResponse] = []
    action_items: List[ActionItemResponse] = []


class ConversationListItem(BaseModel):
    id: str
    title: Optional[str]
    status: str
    location: Optional[str]
    event_name: Optional[str]
    started_at: datetime
    created_at: datetime
    participant_count: int


class AnalysisResult(BaseModel):
    conversation_id: str
    analysis: Dict[str, Any]
    execution_time: float
    timestamp: datetime


# Initialize orchestrator (will be set during app startup)
orchestrator_instance: Optional[AgentOrchestrator] = None


def set_conversation_orchestrator(orchestrator: AgentOrchestrator):
    """Set the orchestrator instance."""
    global orchestrator_instance
    orchestrator_instance = orchestrator


@router.post("", response_model=ConversationResponse, status_code=201)
async def create_conversation(
    request: ConversationCreate
) -> ConversationResponse:
    """
    Create a new conversation by uploading transcript to GCS.

    Args:
        request: Conversation creation request

    Returns:
        Created conversation
    """
    try:
        # Generate ID
        import uuid
        conversation_id = str(uuid.uuid4())

        # Create file name from title or generate one
        file_name = request.title.replace(' ', '_') if request.title else f"transcript_{conversation_id[:8]}"
        file_name = f"{file_name}.txt"

        # Upload transcript to GCS
        success = transcript_storage.upload_transcript(file_name, request.transcript)

        if not success:
            raise HTTPException(status_code=500, detail="Failed to upload transcript to GCS")

        # Return conversation response
        return ConversationResponse(
            id=conversation_id,
            user_id="default_user",
            title=request.title or file_name,
            transcript=request.transcript,
            status=request.status,
            recording_url=request.recording_url,
            location=request.location,
            event_name=request.event_name,
            started_at=request.started_at or datetime.utcnow(),
            ended_at=request.ended_at,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            participants=[],
            entities=[],
            action_items=[]
        )

    except Exception as e:
        logger.error(f"Error creating conversation: {e}")
        raise HTTPException(status_code=500, detail=f"Error creating conversation: {str(e)}")


@router.get("", response_model=List[ConversationListItem])
async def list_conversations(
    status: Optional[str] = None,
    limit: int = 50,
    offset: int = 0
) -> List[ConversationListItem]:
    """
    List conversations from GCS transcripts folder.

    Args:
        status: Filter by status (not used for GCS)
        limit: Maximum number of conversations to return
        offset: Number of conversations to skip

    Returns:
        List of conversations from transcripts
    """
    try:
        # Get transcripts from GCS
        transcripts = transcript_storage.list_transcripts()

        # Apply pagination
        start = offset
        end = offset + limit
        transcripts = transcripts[start:end]

        # Convert to response format
        response = []
        for transcript in transcripts:
            response.append(ConversationListItem(
                id=transcript['id'],
                title=transcript.get('title', transcript['file_name']),
                status=transcript.get('status', 'active'),
                location=transcript.get('location'),
                event_name=transcript.get('event_name'),
                started_at=datetime.fromisoformat(transcript['created_at']) if transcript.get('created_at') else datetime.utcnow(),
                created_at=datetime.fromisoformat(transcript['created_at']) if transcript.get('created_at') else datetime.utcnow(),
                participant_count=0  # Will be populated after analysis
            ))

        logger.info(f"Listed {len(response)} conversations from GCS")
        return response
        
    except Exception as e:
        logger.error(f"Error listing conversations: {e}")
        raise HTTPException(status_code=500, detail=f"Error listing conversations: {str(e)}")


@router.get("/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(
    conversation_id: str
) -> ConversationResponse:
    """
    Get a specific conversation from GCS transcripts.

    Args:
        conversation_id: Conversation/Transcript ID

    Returns:
        Conversation detail from transcript
    """
    try:
        # Get transcript from GCS
        transcript = transcript_storage.get_transcript(conversation_id)

        if not transcript:
            raise HTTPException(status_code=404, detail="Conversation not found")

        # Convert to response format
        return ConversationResponse(
            id=transcript['id'],
            user_id=transcript.get('user_id', 'default_user'),
            title=transcript.get('title', transcript['file_name']),
            transcript=transcript['transcript'],
            status=transcript.get('status', 'active'),
            recording_url=transcript.get('recording_url'),
            location=transcript.get('location'),
            event_name=transcript.get('event_name'),
            started_at=datetime.fromisoformat(transcript['created_at']) if transcript.get('created_at') else datetime.utcnow(),
            ended_at=datetime.fromisoformat(transcript['updated_at']) if transcript.get('updated_at') else None,
            created_at=datetime.fromisoformat(transcript['created_at']) if transcript.get('created_at') else datetime.utcnow(),
            updated_at=datetime.fromisoformat(transcript['updated_at']) if transcript.get('updated_at') else datetime.utcnow(),
            participants=[],  # Will be populated after analysis
            entities=[],  # Will be populated after analysis
            action_items=[]  # Will be populated after analysis
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting conversation: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting conversation: {str(e)}")


@router.put("/{conversation_id}", response_model=ConversationResponse)
async def update_conversation(
    conversation_id: str,
    request: ConversationUpdate,
    db: AsyncSession = Depends(get_db_session)
) -> ConversationResponse:
    """
    Update a conversation.
    
    Args:
        conversation_id: Conversation ID
        request: Conversation update request
        db: Database session
        
    Returns:
        Updated conversation
    """
    try:
        result = await db.execute(
            select(Conversation).where(Conversation.id == conversation_id)
        )
        conversation = result.scalar_one_or_none()
        
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        # Update fields
        update_data = request.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(conversation, field, value)
        
        await db.commit()
        await db.refresh(conversation)
        
        return _conversation_to_response(conversation)
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error updating conversation: {e}")
        raise HTTPException(status_code=500, detail=f"Error updating conversation: {str(e)}")


@router.delete("/{conversation_id}", status_code=204)
async def delete_conversation(
    conversation_id: str,
    db: AsyncSession = Depends(get_db_session)
):
    """
    Delete a conversation.
    
    Args:
        conversation_id: Conversation ID
        db: Database session
    """
    try:
        result = await db.execute(
            select(Conversation).where(Conversation.id == conversation_id)
        )
        conversation = result.scalar_one_or_none()
        
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        await db.delete(conversation)
        await db.commit()
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error deleting conversation: {e}")
        raise HTTPException(status_code=500, detail=f"Error deleting conversation: {str(e)}")


@router.post("/{conversation_id}/analyze", response_model=AnalysisResult)
async def analyze_conversation(
    conversation_id: str,
    db: AsyncSession = Depends(get_db_session)
) -> AnalysisResult:
    """
    Run all agents on a conversation to analyze it.
    
    Args:
        conversation_id: Conversation ID
        db: Database session
        
    Returns:
        Analysis result from all agents
    """
    if not orchestrator_instance:
        raise HTTPException(
            status_code=500,
            detail="Orchestrator not initialized. Please check server startup."
        )
    
    try:
        import time
        start_time = time.time()
        
        # Get conversation
        result = await db.execute(
            select(Conversation).where(Conversation.id == conversation_id)
        )
        conversation = result.scalar_one_or_none()
        
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        if not conversation.transcript:
            raise HTTPException(status_code=400, detail="Conversation has no transcript")
        
        # Run orchestrator with all agents
        query = f"Analyze this conversation:\n\n{conversation.transcript}"
        
        # All available agents
        all_agents = [
            "PerceptionAgent",
            "ContextUnderstandingAgent",
            "PrivacyGuardianAgent",
            "StrategicNetworkingAgent",
            "FollowUpAgent"
        ]
        
        orchestration_result = await orchestrator_instance.execute_agents(
            query=query,
            selected_agents=all_agents,
            conversation_id=conversation_id,
            context=conversation.transcript
        )
        
        execution_time = time.time() - start_time
        
        return AnalysisResult(
            conversation_id=conversation_id,
            analysis=orchestration_result,
            execution_time=execution_time,
            timestamp=datetime.utcnow()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing conversation: {e}")
        raise HTTPException(status_code=500, detail=f"Error analyzing conversation: {str(e)}")


def _conversation_to_response(conversation: Conversation) -> ConversationResponse:
    """Convert a Conversation model to ConversationResponse."""
    from sqlalchemy.inspection import inspect

    # Check if relationships are loaded to avoid lazy loading in async context
    insp = inspect(conversation)
    participants_loaded = 'participants' not in insp.unloaded
    entities_loaded = 'entities' not in insp.unloaded
    action_items_loaded = 'action_items' not in insp.unloaded

    return ConversationResponse(
        id=conversation.id,
        user_id=conversation.user_id,
        title=conversation.title,
        status=conversation.status,
        transcript=conversation.transcript,
        recording_url=conversation.recording_url,
        location=conversation.location,
        event_name=conversation.event_name,
        started_at=conversation.started_at,
        ended_at=conversation.ended_at,
        created_at=conversation.created_at,
        updated_at=conversation.updated_at,
        participants=[
            ParticipantResponse(
                id=p.id,
                name=p.name,
                email=p.email,
                company=p.company,
                title=p.title,
                linkedin_url=p.linkedin_url,
                phone=p.phone,
                consent_status=p.consent_status,
                lead_priority=p.lead_priority,
                lead_score=p.lead_score
            )
            for p in conversation.participants
        ] if participants_loaded else [],
        entities=[
            EntityResponse(
                id=e.id,
                entity_type=e.entity_type,
                entity_value=e.entity_value,
                confidence=e.confidence,
                context=e.context
            )
            for e in conversation.entities
        ] if entities_loaded else [],
        action_items=[
            ActionItemResponse(
                id=a.id,
                description=a.description,
                responsible_party=a.responsible_party,
                due_date=a.due_date,
                completed=a.completed
            )
            for a in conversation.action_items
        ] if action_items_loaded else []
    )
