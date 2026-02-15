"""
Audio processing API endpoints for transcription and speaker diarization.
Critical P1 component for the audio streaming pipeline.
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import logging
import numpy as np
import librosa

from db.session import get_db_session
from db.models import Conversation, Participant
from services.audio_processor import AudioProcessor, DiarizedTranscript
from utils.logger import setup_logger

logger = setup_logger(__name__)
router = APIRouter(prefix="/audio", tags=["Audio Processing"])


# Pydantic models
class SpeakerSegmentResponse(BaseModel):
    """A segment of speech from a single speaker."""
    speaker_id: int
    start_time: float
    end_time: float
    text: str
    confidence: float


class DiarizedTranscriptResponse(BaseModel):
    """Complete diarized transcript with speaker information."""
    conversation_id: str
    segments: List[SpeakerSegmentResponse]
    speaker_count: int
    speaker_names: dict
    total_duration: float
    formatted_transcript: str
    speaker_stats: dict
    created_at: datetime


class AudioUploadResponse(BaseModel):
    """Response for audio upload and processing."""
    conversation_id: str
    transcript: DiarizedTranscriptResponse
    message: str


# Initialize audio processor (lazy loaded)
audio_processor_instance: Optional[AudioProcessor] = None


def get_audio_processor() -> AudioProcessor:
    """Get or initialize the audio processor."""
    global audio_processor_instance
    if audio_processor_instance is None:
        logger.info("Initializing audio processor...")
        audio_processor_instance = AudioProcessor()
    return audio_processor_instance


@router.post("/process", response_model=AudioUploadResponse, status_code=200)
async def process_audio_file(
    file: UploadFile = File(...),
    conversation_id: Optional[str] = None,
    db: AsyncSession = Depends(get_db_session)
) -> AudioUploadResponse:
    """
    Upload and process audio file for transcription and speaker diarization.

    This endpoint:
    1. Accepts audio file (WAV, MP3, FLAC, etc.)
    2. Converts to PCM 16kHz mono
    3. Runs Whisper transcription
    4. Runs Pyannote speaker diarization
    5. Matches speakers to transcript segments
    6. Stores conversation with diarized transcript

    Args:
        file: Audio file upload
        conversation_id: Optional existing conversation to update
        db: Database session

    Returns:
        AudioUploadResponse with diarized transcript
    """
    try:
        # Validate file
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file provided")

        if not _is_audio_file(file.filename):
            raise HTTPException(
                status_code=400,
                detail="Invalid file format. Supported: WAV, MP3, FLAC, OGG, M4A"
            )

        # Load and preprocess audio
        logger.info(f"Loading audio file: {file.filename}")
        audio_data, sample_rate = await _load_audio_file(file)

        # Process audio (transcribe + diarize)
        logger.info("Starting audio processing (transcription + diarization)...")
        processor = get_audio_processor()
        diarized_transcript = await processor.process_audio_stream(audio_data, sample_rate)

        # Set conversation ID
        diarized_transcript.conversation_id = conversation_id or diarized_transcript.conversation_id

        # Save to database or update existing conversation
        logger.info(f"Saving conversation to database: {diarized_transcript.conversation_id}")
        await _save_conversation(
            db=db,
            diarized_transcript=diarized_transcript,
            filename=file.filename
        )

        # Format and generate statistics
        formatted = processor.format_transcript(diarized_transcript)
        stats = processor.get_speaker_stats(diarized_transcript)

        # Build response
        segments_response = [
            SpeakerSegmentResponse(
                speaker_id=seg.speaker_id,
                start_time=seg.start_time,
                end_time=seg.end_time,
                text=seg.text,
                confidence=seg.confidence
            )
            for seg in diarized_transcript.segments
        ]

        transcript_response = DiarizedTranscriptResponse(
            conversation_id=diarized_transcript.conversation_id,
            segments=segments_response,
            speaker_count=diarized_transcript.speaker_count,
            speaker_names=diarized_transcript.speaker_names,
            total_duration=diarized_transcript.total_duration,
            formatted_transcript=formatted,
            speaker_stats={
                str(k): v for k, v in stats.items()
            },
            created_at=diarized_transcript.created_at
        )

        return AudioUploadResponse(
            conversation_id=diarized_transcript.conversation_id,
            transcript=transcript_response,
            message=f"Successfully processed audio with {diarized_transcript.speaker_count} speakers"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing audio: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error processing audio: {str(e)}")


@router.get("/speakers/{conversation_id}")
async def get_speakers(
    conversation_id: str,
    db: AsyncSession = Depends(get_db_session)
):
    """
    Get speaker information for a conversation.

    Args:
        conversation_id: Conversation ID
        db: Database session

    Returns:
        List of speakers with their statistics
    """
    try:
        from sqlalchemy import select

        result = await db.execute(
            select(Conversation).where(Conversation.id == conversation_id)
        )
        conversation = result.scalar_one_or_none()

        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")

        # Get participants (speakers) from database
        participant_result = await db.execute(
            select(Participant).where(Participant.conversation_id == conversation_id)
        )
        participants = participant_result.scalars().all()

        speakers = [
            {
                "speaker_id": idx,
                "name": p.name or f"Speaker {idx}",
                "email": p.email,
                "company": p.company,
                "title": p.title,
                "linkedin_url": p.linkedin_url,
                "consent_status": p.consent_status
            }
            for idx, p in enumerate(participants, 1)
        ]

        return {
            "conversation_id": conversation_id,
            "speaker_count": len(speakers),
            "speakers": speakers
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting speakers: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting speakers: {str(e)}")


@router.post("/identify-speakers/{conversation_id}")
async def identify_speakers(
    conversation_id: str,
    speaker_info: dict,
    db: AsyncSession = Depends(get_db_session)
):
    """
    Manually identify speakers in a conversation.

    Example body:
    {
        "speakers": {
            "1": {"name": "John Doe", "email": "john@example.com", "company": "Acme Corp"},
            "2": {"name": "Jane Smith", "email": "jane@example.com", "company": "Tech Inc"}
        }
    }

    Args:
        conversation_id: Conversation ID
        speaker_info: Speaker identification information
        db: Database session

    Returns:
        Updated conversation with identified speakers
    """
    try:
        from sqlalchemy import select

        result = await db.execute(
            select(Conversation).where(Conversation.id == conversation_id)
        )
        conversation = result.scalar_one_or_none()

        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")

        speakers = speaker_info.get("speakers", {})

        # Create or update participants for each speaker
        for speaker_id, info in speakers.items():
            participant = Participant(
                conversation_id=conversation_id,
                name=info.get("name"),
                email=info.get("email"),
                company=info.get("company"),
                title=info.get("title"),
                linkedin_url=info.get("linkedin_url"),
                phone=info.get("phone")
            )
            db.add(participant)

        await db.commit()
        logger.info(f"Identified {len(speakers)} speakers for conversation {conversation_id}")

        return {
            "conversation_id": conversation_id,
            "speaker_count": len(speakers),
            "message": f"Successfully identified {len(speakers)} speakers"
        }

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error identifying speakers: {e}")
        raise HTTPException(status_code=500, detail=f"Error identifying speakers: {str(e)}")


# Helper functions

def _is_audio_file(filename: str) -> bool:
    """Check if file has valid audio extension."""
    valid_extensions = {".wav", ".mp3", ".flac", ".ogg", ".m4a", ".aac", ".wma"}
    return any(filename.lower().endswith(ext) for ext in valid_extensions)


async def _load_audio_file(file: UploadFile) -> tuple[np.ndarray, int]:
    """
    Load audio file and convert to PCM 16kHz mono.

    Args:
        file: Uploaded file

    Returns:
        Tuple of (audio_data, sample_rate)
    """
    try:
        # Read file contents
        content = await file.read()

        # Load with librosa (handles multiple formats)
        # target_sr=16000 for ASR models
        # mono=True for speaker diarization
        audio_data, sample_rate = librosa.load(
            content,
            sr=16000,
            mono=True
        )

        # Normalize to [-1, 1] range (float32)
        audio_data = audio_data.astype(np.float32)

        logger.info(
            f"Loaded audio: {len(audio_data)} samples, "
            f"sr={sample_rate}, duration={len(audio_data)/sample_rate:.1f}s"
        )

        return audio_data, sample_rate

    except Exception as e:
        logger.error(f"Error loading audio file: {e}")
        raise HTTPException(status_code=400, detail=f"Error loading audio file: {str(e)}")


async def _save_conversation(
    db: AsyncSession,
    diarized_transcript: DiarizedTranscript,
    filename: str
) -> str:
    """
    Save conversation with diarized transcript to database.

    Args:
        db: Database session
        diarized_transcript: Processed transcript
        filename: Original audio filename

    Returns:
        Conversation ID
    """
    try:
        from sqlalchemy import select

        # Check if conversation exists
        result = await db.execute(
            select(Conversation).where(Conversation.id == diarized_transcript.conversation_id)
        )
        conversation = result.scalar_one_or_none()

        # Format transcript as readable text
        formatted_transcript = _build_readable_transcript(diarized_transcript)

        if conversation:
            # Update existing conversation
            conversation.transcript = formatted_transcript
            conversation.status = "completed"
            conversation.ended_at = datetime.utcnow()
        else:
            # Create new conversation
            conversation = Conversation(
                id=diarized_transcript.conversation_id,
                user_id="default_user",  # TODO: Get from auth context
                title=filename.rsplit(".", 1)[0],  # Use filename as title
                transcript=formatted_transcript,
                status="completed",
                started_at=datetime.utcnow(),
                ended_at=datetime.utcnow()
            )
            db.add(conversation)

        # Create participants for each speaker
        # First delete existing participants for this conversation
        from sqlalchemy import delete
        await db.execute(
            delete(Participant).where(Participant.conversation_id == conversation.id)
        )

        # Create new participants
        for speaker_id, speaker_name in diarized_transcript.speaker_names.items():
            participant = Participant(
                conversation_id=conversation.id,
                name=speaker_name,
                consent_status="unknown"
            )
            db.add(participant)

        await db.commit()
        logger.info(f"Saved conversation {conversation.id}")

        return conversation.id

    except Exception as e:
        await db.rollback()
        logger.error(f"Error saving conversation: {e}")
        raise


def _build_readable_transcript(diarized: DiarizedTranscript) -> str:
    """
    Build human-readable transcript from diarized segments.

    Format:
    Speaker 1: Hello everyone!
    Speaker 2: Hi there!
    """
    lines = []
    for seg in diarized.segments:
        speaker_name = diarized.speaker_names.get(seg.speaker_id, f"Speaker {seg.speaker_id}")
        lines.append(f"{speaker_name}: {seg.text}")

    return "\n".join(lines)
