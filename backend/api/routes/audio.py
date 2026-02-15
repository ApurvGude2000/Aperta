"""
Audio processing API endpoints for transcription and speaker diarization.
Critical P1 component for the audio streaming pipeline.
"""

from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import List, Optional, TYPE_CHECKING
from datetime import datetime
import logging
import numpy as np
import uuid
import json
import librosa

from db.session import get_db_session
from db.models import Conversation, Participant, AudioRecording, Transcription
from services.storage import StorageService, StorageConfig
from config import settings
from utils.logger import setup_logger

if TYPE_CHECKING:
    from services.audio_processor import DiarizedTranscript

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


class TranscriptionSegment(BaseModel):
    """Segment of transcribed speech."""
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


class TranscriptionDetailResponse(BaseModel):
    """Detailed transcription with analysis results."""
    id: str
    recording_id: str
    conversation_id: str
    raw_text: Optional[str]
    formatted_text: Optional[str]
    speaker_count: int
    speaker_names: dict
    segments: list
    confidence_score: Optional[float]
    sentiment: Optional[str]
    summary: Optional[str]
    entities: list
    action_items: list
    transcript_file_path: Optional[str]
    created_at: datetime


class AudioRecordingResponse(BaseModel):
    """Audio recording with transcription data."""
    id: str
    conversation_id: str
    file_path: str
    file_size: int
    file_format: str
    duration: float
    original_filename: str
    processing_status: str
    created_at: datetime
    transcription: Optional[TranscriptionDetailResponse] = None


class EventAudioProcessResponse(BaseModel):
    """Response for processing audio from an event."""
    conversation_id: str
    audio_recording: AudioRecordingResponse
    transcription: TranscriptionDetailResponse
    ai_analysis: dict
    message: str


class AudioUploadResponse(BaseModel):
    """Response for audio upload and processing."""
    conversation_id: str
    transcript: DiarizedTranscriptResponse
    audio_file_path: str
    transcript_file_path: str
    message: str


class StorageInfo(BaseModel):
    """Storage configuration info."""
    storage_type: str
    local_path: Optional[str]
    gcp_bucket: Optional[str]
    gcp_enabled: bool


# Initialize audio processor (lazy loaded)
audio_processor_instance: Optional = None
storage_instance: Optional[StorageService] = None


def get_audio_processor():
    """Get or initialize the audio processor (lazy import)."""
    global audio_processor_instance
    if audio_processor_instance is None:
        logger.info("Initializing audio processor...")
        from services.audio_processor import AudioProcessor
        audio_processor_instance = AudioProcessor()
    return audio_processor_instance


def get_storage_service() -> StorageService:
    """Get or initialize the storage service."""
    global storage_instance
    if storage_instance is None:
        logger.info("Initializing storage service...")

        # Check if GCP should be used
        use_gcp = bool(
            settings.gcp_bucket_name
            and settings.gcp_service_account_json
        )

        config = StorageConfig(
            local_storage_path="./uploads",
            use_gcp=use_gcp,
            gcp_bucket=settings.gcp_bucket_name if use_gcp else None,
            gcp_project_id=settings.gcp_project_id if use_gcp else None,
            gcp_service_account_json=settings.gcp_service_account_json if use_gcp else None,
        )
        storage_instance = StorageService(config)
    return storage_instance


async def _get_optional_db_session() -> Optional[AsyncSession]:
    """Get database session, but fail gracefully if database is unavailable."""
    try:
        from db.session import get_db_session as get_db
        async for session in get_db():
            return session
    except Exception as e:
        logger.warning(f"Database session unavailable, running in offline mode: {e}")
        return None


@router.post("/process", response_model=AudioUploadResponse, status_code=200)
async def process_audio_file(
    file: UploadFile = File(...),
    conversation_id: Optional[str] = None,
    db: Optional[AsyncSession] = Depends(lambda: _get_optional_db_session())
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
        audio_bytes = await file.read()
        audio_data, sample_rate = await _load_audio_file_from_bytes(audio_bytes)

        # Generate conversation ID if not provided
        conv_id = conversation_id or f"conv_{uuid.uuid4().hex[:12]}"

        # Process audio (transcribe + diarize)
        logger.info("Starting audio processing (transcription + diarization)...")
        processor = get_audio_processor()
        diarized_transcript = await processor.process_audio_stream(audio_data, sample_rate)
        diarized_transcript.conversation_id = conv_id

        # Format and generate statistics
        formatted = processor.format_transcript(diarized_transcript)
        stats = processor.get_speaker_stats(diarized_transcript)

        # Save audio file to storage
        logger.info(f"Saving audio file to storage...")
        storage = get_storage_service()
        audio_file_path = await storage.save_audio_file(
            file_content=audio_bytes,
            conversation_id=conv_id,
            filename=file.filename,
            metadata={
                "duration": diarized_transcript.total_duration,
                "speaker_count": diarized_transcript.speaker_count,
                "uploaded_at": datetime.utcnow().isoformat(),
            },
        )

        # Run PII redaction on transcript
        logger.info(f"Running PII Guardian to protect transcript...")
        privacy_agent = PrivacyGuardianAgent()
        redacted_transcript = await privacy_agent.redact_transcript(formatted)

        # Save ORIGINAL transcript to storage (for agent parsing)
        logger.info(f"Saving original transcript to storage (for agents)...")
        transcript_file_path = await storage.save_transcript(
            transcript_text=formatted,
            conversation_id=conv_id,
            format="txt",
            folder="transcripts",  # Original for agent parsing
        )

        # Save PII-REDACTED transcript to storage (outward-facing for users)
        logger.info(f"Saving PII-redacted transcript to storage (for users)...")
        clean_transcript_file_path = await storage.save_transcript(
            transcript_text=redacted_transcript,
            conversation_id=conv_id,
            format="txt",
            folder="transcripts-clean",  # Clean version for users
        )

        # Save to database (optional - fails gracefully if database unavailable)
        if db:
            try:
                logger.info(f"Saving conversation to database: {conv_id}")
                await _save_conversation(
                    db=db,
                    conversation_id=conv_id,
                    diarized_transcript=diarized_transcript,
                    filename=file.filename,
                    audio_file_path=audio_file_path,
                    transcript_file_path=transcript_file_path,
                )
            except Exception as e:
                logger.warning(f"Failed to save to database: {e}. Audio files still saved to filesystem.")
        else:
            logger.info("Database unavailable - audio files saved to filesystem only")

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
            audio_file_path=audio_file_path,
            transcript_file_path=transcript_file_path,
            message=f"Successfully processed audio with {diarized_transcript.speaker_count} speakers and saved to storage"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing audio: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error processing audio: {str(e)}")


@router.post("/process-event", response_model=EventAudioProcessResponse, status_code=200)
async def process_event_audio(
    file: UploadFile = File(...),
    event_name: str = Form(...),
    conversation_id: Optional[str] = Form(None),
    location: Optional[str] = Form(None),
    db: Optional[AsyncSession] = Depends(lambda: _get_optional_db_session())
) -> EventAudioProcessResponse:
    """
    Process audio file from an event with full AI analysis.

    This endpoint:
    1. Accepts audio file from iOS app or web
    2. Runs transcription and speaker diarization
    3. Appends transcript to event's transcript file
    4. Runs AI agents for entity extraction, sentiment analysis
    5. Stores everything with proper relationships
    6. Returns comprehensive analysis

    Args:
        file: Audio file upload
        event_name: Name of the event (REQUIRED - determines transcript file)
        conversation_id: Optional existing conversation ID
        location: Event location
        db: Database session

    Returns:
        EventAudioProcessResponse with full analysis
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

        if not event_name:
            raise HTTPException(status_code=400, detail="event_name is required")

        # Load and preprocess audio
        logger.info(f"Loading audio file: {file.filename}")
        audio_bytes = await file.read()
        audio_data, sample_rate = await _load_audio_file_from_bytes(audio_bytes)

        # Generate conversation ID if not provided
        conv_id = conversation_id or f"conv_{uuid.uuid4().hex[:12]}"

        # Process audio (transcribe + diarize)
        logger.info("Starting audio processing (transcription + diarization)...")
        processor = get_audio_processor()
        diarized_transcript = await processor.process_audio_stream(audio_data, sample_rate)
        diarized_transcript.conversation_id = conv_id

        # Format transcript
        formatted = processor.format_transcript(diarized_transcript)
        stats = processor.get_speaker_stats(diarized_transcript)

        # NOTE: Audio files are NOT saved for privacy reasons
        # PII redaction happens on mobile before upload

        # Append transcript to event's transcript file
        logger.info(f"Appending transcript to event file: transcripts/{event_name}.txt")
        storage = get_storage_service()
        transcript_file_path = await storage.append_transcript(
            transcript_text=formatted,
            event_name=event_name,
        )

        # Run AI agents for analysis
        logger.info("Running AI agents for analysis...")
        ai_analysis = await _run_audio_analysis_agents(formatted)

        # No audio file saved (privacy)
        audio_file_path = None

        # Save to database
        recording_id = None
        transcription_id = None
        if db:
            try:
                logger.info(f"Saving transcription to database: {conv_id}")
                recording_id, transcription_id = await _save_event_audio_with_analysis(
                    db=db,
                    conversation_id=conv_id,
                    diarized_transcript=diarized_transcript,
                    filename=file.filename,
                    audio_file_path=None,  # Not saved for privacy
                    transcript_file_path=transcript_file_path,
                    audio_bytes=audio_bytes,
                    event_name=event_name,
                    location=location,
                    ai_analysis=ai_analysis,
                )
            except Exception as e:
                logger.warning(f"Failed to save to database: {e}. Transcript still saved to GCS.")
        else:
            logger.info("Database unavailable - transcript saved to GCS only")

        # Build response
        audio_recording = AudioRecordingResponse(
            id=recording_id or f"rec_{uuid.uuid4().hex[:12]}",
            conversation_id=conv_id,
            file_path="",  # No audio file for privacy
            file_size=len(audio_bytes),
            file_format=file.filename.split(".")[-1].lower(),
            duration=diarized_transcript.total_duration,
            original_filename=file.filename,
            processing_status="completed",
            created_at=datetime.utcnow(),
        )

        transcription_response = TranscriptionDetailResponse(
            id=transcription_id or f"trans_{uuid.uuid4().hex[:12]}",
            recording_id=audio_recording.id,
            conversation_id=conv_id,
            raw_text=formatted,
            formatted_text=formatted,
            speaker_count=diarized_transcript.speaker_count,
            speaker_names=diarized_transcript.speaker_names,
            segments=[
                {
                    "speaker_id": seg.speaker_id,
                    "start_time": seg.start_time,
                    "end_time": seg.end_time,
                    "text": seg.text,
                    "confidence": seg.confidence,
                }
                for seg in diarized_transcript.segments
            ],
            confidence_score=ai_analysis.get("confidence_score"),
            sentiment=ai_analysis.get("sentiment"),
            summary=ai_analysis.get("summary"),
            entities=ai_analysis.get("entities", []),
            action_items=ai_analysis.get("action_items", []),
            transcript_file_path=transcript_file_path,
            created_at=datetime.utcnow(),
        )

        return EventAudioProcessResponse(
            conversation_id=conv_id,
            audio_recording=audio_recording,
            transcription=transcription_response,
            ai_analysis=ai_analysis,
            message=f"Successfully processed event audio with {diarized_transcript.speaker_count} speakers"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing event audio: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error processing event audio: {str(e)}")


@router.get("/speakers/{conversation_id}")
async def get_speakers(
    conversation_id: str,
    db: Optional[AsyncSession] = Depends(lambda: _get_optional_db_session())
):
    """
    Get speaker information for a conversation.

    Args:
        conversation_id: Conversation ID
        db: Database session

    Returns:
        List of speakers with their statistics
    """
    if not db:
        raise HTTPException(status_code=503, detail="Database service unavailable")

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


@router.get("/storage-info", response_model=StorageInfo)
async def get_storage_info() -> StorageInfo:
    """
    Get storage configuration information.

    Returns:
        Storage info (type, paths, S3 status, etc.)
    """
    try:
        storage = get_storage_service()
        info = storage.get_storage_info()

        return StorageInfo(
            storage_type=info["storage_type"],
            local_path=info["local_path"],
            s3_bucket=info["s3_bucket"],
            s3_enabled=info["s3_enabled"],
        )

    except Exception as e:
        logger.error(f"Error getting storage info: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting storage info: {str(e)}")


@router.post("/append-transcript")
async def append_transcript_only(
    transcript_text: str = Form(...),
    event_name: str = Form(...),
    location: Optional[str] = Form(None),
):
    """
    Append transcript text to event's transcript file.
    NO audio file required - transcript is already generated on mobile.
    PII redaction happens on mobile before upload.

    Args:
        transcript_text: Pre-redacted transcript text from mobile
        event_name: Name of the event (determines transcript file)
        location: Event location (optional)

    Returns:
        Success message with transcript file path
    """
    try:
        logger.info(f"Appending transcript to event: {event_name}")

        # Append to transcript file
        storage = get_storage_service()
        transcript_file_path = await storage.append_transcript(
            transcript_text=transcript_text,
            event_name=event_name,
        )

        return {
            "message": f"Successfully appended transcript to {event_name}",
            "transcript_file_path": transcript_file_path,
            "event_name": event_name,
            "location": location,
            "character_count": len(transcript_text)
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error appending transcript: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error appending transcript: {str(e)}")


@router.post("/identify-speakers/{conversation_id}")
async def identify_speakers(
    conversation_id: str,
    speaker_info: dict,
    db: Optional[AsyncSession] = Depends(lambda: _get_optional_db_session())
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
    if not db:
        raise HTTPException(status_code=503, detail="Database service unavailable")

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


async def _load_audio_file_from_bytes(content: bytes) -> tuple[np.ndarray, int]:
    """
    Load audio from bytes and convert to PCM 16kHz mono.

    Args:
        content: Raw audio file bytes

    Returns:
        Tuple of (audio_data, sample_rate)
    """
    import tempfile
    import os

    temp_file = None
    try:
        # Save to temp file so librosa can detect format
        with tempfile.NamedTemporaryFile(delete=False, suffix='.audio') as f:
            f.write(content)
            temp_file = f.name

        # Load with librosa (handles multiple formats)
        # target_sr=16000 for ASR models
        # mono=True for speaker diarization
        audio_data, sample_rate = librosa.load(
            temp_file,
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
    finally:
        # Clean up temp file
        if temp_file and os.path.exists(temp_file):
            try:
                os.remove(temp_file)
            except:
                pass


async def _save_conversation(
    db: AsyncSession,
    conversation_id: str,
    diarized_transcript: "DiarizedTranscript",
    filename: str,
    audio_file_path: Optional[str],
    transcript_file_path: str,
) -> str:
    """
    Save conversation with diarized transcript to database.

    Args:
        db: Database session
        conversation_id: Conversation ID
        diarized_transcript: Processed transcript
        filename: Original audio filename
        audio_file_path: Path where audio was saved (None if not saved for privacy)
        transcript_file_path: Path where transcript was saved

    Returns:
        Conversation ID
    """
    try:
        # Check if conversation exists
        result = await db.execute(
            select(Conversation).where(Conversation.id == conversation_id)
        )
        conversation = result.scalar_one_or_none()

        # Format transcript as readable text
        formatted_transcript = _build_readable_transcript(diarized_transcript)

        if conversation:
            # Update existing conversation
            conversation.transcript = formatted_transcript
            conversation.recording_url = audio_file_path or ""  # Empty if not saved
            conversation.status = "completed"
            conversation.ended_at = datetime.utcnow()
        else:
            # Create new conversation
            conversation = Conversation(
                id=conversation_id,
                user_id="default_user",  # TODO: Get from auth context
                title=filename.rsplit(".", 1)[0],  # Use filename as title
                transcript=formatted_transcript,
                recording_url=audio_file_path or "",  # Empty if not saved
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
        if audio_file_path:
            logger.info(f"  Audio saved to: {audio_file_path}")
        else:
            logger.info(f"  Audio NOT saved (privacy)")
        logger.info(f"  Transcript saved to: {transcript_file_path}")

        return conversation.id

    except Exception as e:
        await db.rollback()
        logger.error(f"Error saving conversation: {e}")
        raise


def _build_readable_transcript(diarized: "DiarizedTranscript") -> str:
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


async def _run_audio_analysis_agents(formatted_transcript: str) -> dict:
    """
    Run AI agents to analyze the transcribed audio.

    Args:
        formatted_transcript: Formatted transcript text

    Returns:
        Dictionary with analysis results
    """
    try:
        from anthropic import Anthropic
        client = Anthropic()

        # Use Claude to extract entities, action items, sentiment, and generate summary
        analysis_prompt = f"""Analyze this conversation transcript and provide:
1. A brief summary (1-2 sentences)
2. Overall sentiment (positive, negative, neutral, mixed)
3. Key entities (people, companies, technologies mentioned)
4. Action items and commitments made
5. Confidence score (0-1) for the analysis

Format your response as JSON with keys: summary, sentiment, entities, action_items, confidence_score

Transcript:
{formatted_transcript}"""

        message = client.messages.create(
            model="claude-opus-4-6",
            max_tokens=1024,
            messages=[
                {"role": "user", "content": analysis_prompt}
            ]
        )

        # Parse the response
        response_text = message.content[0].text
        try:
            # Try to parse as JSON
            import json
            analysis = json.loads(response_text)
        except:
            # Fallback if JSON parsing fails
            analysis = {
                "summary": response_text,
                "sentiment": "unknown",
                "entities": [],
                "action_items": [],
                "confidence_score": 0.5
            }

        logger.info(f"Audio analysis completed: {analysis}")
        return analysis

    except Exception as e:
        logger.warning(f"Error running audio analysis agents: {e}")
        return {
            "summary": None,
            "sentiment": None,
            "entities": [],
            "action_items": [],
            "confidence_score": 0.0
        }


async def _save_event_audio_with_analysis(
    db: AsyncSession,
    conversation_id: str,
    diarized_transcript: "DiarizedTranscript",
    filename: str,
    audio_file_path: Optional[str],
    transcript_file_path: str,
    audio_bytes: bytes,
    event_name: Optional[str],
    location: Optional[str],
    ai_analysis: dict,
) -> tuple[str, str]:
    """
    Save audio recording and transcription with AI analysis results to database.

    Args:
        db: Database session
        conversation_id: Conversation ID
        diarized_transcript: Processed transcript
        filename: Original audio filename
        audio_file_path: Path where audio was saved (None if not saved for privacy)
        transcript_file_path: Path where transcript was saved
        audio_bytes: Raw audio bytes
        event_name: Event name
        location: Event location
        ai_analysis: AI analysis results

    Returns:
        Tuple of (recording_id, transcription_id)
    """
    try:
        # Check if conversation exists, create if not
        result = await db.execute(
            select(Conversation).where(Conversation.id == conversation_id)
        )
        conversation = result.scalar_one_or_none()

        if not conversation:
            # Create new conversation
            conversation = Conversation(
                id=conversation_id,
                user_id="default_user",  # TODO: Get from auth context
                title=event_name or filename.rsplit(".", 1)[0],
                status="completed",
                location=location,
                event_name=event_name,
                started_at=datetime.utcnow(),
                ended_at=datetime.utcnow()
            )
            db.add(conversation)
            await db.flush()

        # Create AudioRecording entry
        recording = AudioRecording(
            conversation_id=conversation_id,
            file_path=audio_file_path or "",  # Empty if not saved for privacy
            file_size=len(audio_bytes),
            file_format=filename.split(".")[-1].lower(),
            duration=diarized_transcript.total_duration,
            original_filename=filename,
            uploaded_from="ios_app",
            processing_status="completed"
        )
        db.add(recording)
        await db.flush()

        # Create Transcription entry
        formatted_text = _build_readable_transcript(diarized_transcript)
        transcription = Transcription(
            recording_id=recording.id,
            conversation_id=conversation_id,
            raw_text=formatted_text,
            formatted_text=formatted_text,
            speaker_count=diarized_transcript.speaker_count,
            speaker_names=diarized_transcript.speaker_names,
            segments=[
                {
                    "speaker_id": seg.speaker_id,
                    "start_time": seg.start_time,
                    "end_time": seg.end_time,
                    "text": seg.text,
                    "confidence": seg.confidence,
                }
                for seg in diarized_transcript.segments
            ],
            confidence_score=ai_analysis.get("confidence_score"),
            sentiment=ai_analysis.get("sentiment"),
            summary=ai_analysis.get("summary"),
            entities=ai_analysis.get("entities", []),
            action_items=ai_analysis.get("action_items", []),
            transcript_file_path=transcript_file_path
        )
        db.add(transcription)
        await db.flush()

        # Create participants for each speaker
        from sqlalchemy import delete
        await db.execute(
            delete(Participant).where(Participant.conversation_id == conversation_id)
        )

        for speaker_id, speaker_name in diarized_transcript.speaker_names.items():
            participant = Participant(
                conversation_id=conversation_id,
                name=speaker_name,
                consent_status="unknown"
            )
            db.add(participant)

        await db.commit()
        logger.info(f"Saved audio recording and transcription for {conversation_id}")
        logger.info(f"  Recording ID: {recording.id}")
        logger.info(f"  Transcription ID: {transcription.id}")

        return recording.id, transcription.id

    except Exception as e:
        await db.rollback()
        logger.error(f"Error saving event audio with analysis: {e}")
        raise
