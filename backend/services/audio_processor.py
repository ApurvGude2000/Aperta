"""
Audio Processing Service for Aperta.
Handles transcription, speaker diarization, and audio analysis.
Critical P1 component for the audio streaming pipeline.
"""

import numpy as np
import asyncio
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from datetime import datetime
import torch
import logging

logger = logging.getLogger(__name__)


@dataclass
class SpeakerSegment:
    """Represents a speaker and their time segment in the conversation."""
    speaker_id: int
    start_time: float
    end_time: float
    text: str
    confidence: float = 1.0


@dataclass
class DiarizedTranscript:
    """Complete diarized transcript with speaker information."""
    conversation_id: str
    segments: List[SpeakerSegment]
    speaker_count: int
    speaker_names: Dict[int, str]  # Maps speaker_id to name if available
    total_duration: float
    created_at: datetime


class AudioProcessor:
    """
    On-device audio processor combining transcription and speaker diarization.

    Pipeline:
    1. Audio stream → VAD (Voice Activity Detection)
    2. Audio chunks → Whisper (Transcription) → Text segments
    3. Audio chunks → Pyannote (Speaker embeddings) → Speaker clustering
    4. Combine → Diarized transcript with speaker labels
    """

    def __init__(self):
        """Initialize audio processor with models."""
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.whisper_model = None
        self.diarization_model = None
        self.vad_model = None
        self.is_initialized = False
        self._init_models()

    def _init_models(self):
        """Initialize Whisper, Pyannote, and VAD models."""
        try:
            # Import models lazily to avoid startup delays if not needed
            import whisper
            from pyannote.audio import Pipeline
            from silero_vad import load_silero_vad

            # Load Whisper (small quantized version for mobile)
            logger.info("Loading Whisper model (small)...")
            self.whisper_model = whisper.load_model("small", device=self.device)

            # Load Pyannote speaker diarization pipeline
            # Note: Requires huggingface token. Users must accept license:
            # https://huggingface.co/pyannote/speaker-diarization-3.0
            logger.info("Loading Pyannote speaker diarization pipeline...")
            try:
                self.diarization_model = Pipeline.from_pretrained(
                    "pyannote/speaker-diarization-3.0",
                    use_auth_token=True  # User must set HF_TOKEN env var
                )
                self.diarization_model = self.diarization_model.to(self.device)
            except Exception as e:
                logger.warning(f"Could not load Pyannote model: {e}. Diarization will be limited.")
                self.diarization_model = None

            # Load Silero VAD for voice activity detection
            logger.info("Loading Silero VAD model...")
            self.vad_model = load_silero_vad()

            self.is_initialized = True
            logger.info("Audio processor initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize audio models: {e}")
            raise

    async def process_audio_stream(
        self,
        audio_data: np.ndarray,
        sample_rate: int = 16000
    ) -> DiarizedTranscript:
        """
        Process audio stream: transcribe + diarize simultaneously.

        Args:
            audio_data: Raw audio as numpy array (mono, float32, normalized -1 to 1)
            sample_rate: Sample rate in Hz (default 16000 for ASR models)

        Returns:
            DiarizedTranscript with speaker-labeled segments
        """
        if not self.is_initialized:
            raise RuntimeError("Audio processor not initialized")

        # Run transcription and diarization in parallel
        transcript, duration = await asyncio.gather(
            self._transcribe_audio(audio_data, sample_rate),
            asyncio.get_event_loop().run_in_executor(
                None, self._get_audio_duration, audio_data, sample_rate
            )
        )

        # Get speaker diarization
        diarized_segments = await self._diarize_audio(audio_data, sample_rate, transcript)

        # Build final diarized transcript
        return self._build_diarized_transcript(
            segments=diarized_segments,
            duration=duration
        )

    async def _transcribe_audio(
        self,
        audio_data: np.ndarray,
        sample_rate: int
    ) -> List[Dict[str, Any]]:
        """
        Transcribe audio using Whisper with real-time streaming support.

        Returns list of segments with timestamps and text.
        """
        try:
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                lambda: self.whisper_model.transcribe(
                    audio_data,
                    language="en",
                    fp16=self.device == "cuda",  # Use FP16 on GPU for speed
                )
            )

            # Extract segments with timestamps
            segments = []
            for segment in result.get("segments", []):
                segments.append({
                    "start": segment["start"],
                    "end": segment["end"],
                    "text": segment["text"].strip(),
                    "confidence": segment.get("confidence", 1.0),
                })

            logger.info(f"Transcription complete: {len(segments)} segments")
            return segments

        except Exception as e:
            logger.error(f"Transcription failed: {e}")
            raise

    async def _diarize_audio(
        self,
        audio_data: np.ndarray,
        sample_rate: int,
        transcript_segments: List[Dict[str, Any]]
    ) -> List[SpeakerSegment]:
        """
        Perform speaker diarization using Pyannote and speaker embeddings.

        Returns speaker-labeled segments matched to transcript.
        """
        if not self.diarization_model:
            logger.warning("Diarization model not available, assigning single speaker")
            return [
                SpeakerSegment(
                    speaker_id=1,
                    start_time=seg["start"],
                    end_time=seg["end"],
                    text=seg["text"],
                    confidence=0.5  # Low confidence without proper diarization
                )
                for seg in transcript_segments
            ]

        try:
            loop = asyncio.get_event_loop()

            # Run diarization
            diarization = await loop.run_in_executor(
                None,
                lambda: self.diarization_model({"waveform": torch.tensor(audio_data).unsqueeze(0), "sample_rate": sample_rate})
            )

            # Extract speaker turns
            speaker_turns = self._extract_speaker_turns(diarization)

            # Match transcript segments with speaker turns
            diarized_segments = self._match_speakers_to_transcript(
                transcript_segments, speaker_turns
            )

            logger.info(f"Diarization complete: {len(speaker_turns)} speaker turns")
            return diarized_segments

        except Exception as e:
            logger.error(f"Diarization failed: {e}")
            # Fallback: assign single speaker
            return [
                SpeakerSegment(
                    speaker_id=1,
                    start_time=seg["start"],
                    end_time=seg["end"],
                    text=seg["text"],
                    confidence=0.3
                )
                for seg in transcript_segments
            ]

    def _extract_speaker_turns(self, diarization: Any) -> List[Tuple[float, float, str]]:
        """
        Extract speaker turns from Pyannote diarization output.

        Returns list of (start_time, end_time, speaker_id) tuples.
        """
        turns = []
        for turn, _, speaker in diarization.itertracks(yield_label=True):
            turns.append((float(turn.start), float(turn.end), speaker))
        return turns

    def _match_speakers_to_transcript(
        self,
        transcript_segments: List[Dict[str, Any]],
        speaker_turns: List[Tuple[float, float, str]]
    ) -> List[SpeakerSegment]:
        """
        Match transcript segments with speaker turns using time overlap.

        Uses greedy matching: for each transcript segment, find the speaker
        turn with maximum time overlap.
        """
        diarized = []
        speaker_map = {}  # Maps speaker labels to numeric IDs
        next_speaker_id = 1

        for seg in transcript_segments:
            seg_start, seg_end = seg["start"], seg["end"]
            seg_mid = (seg_start + seg_end) / 2

            # Find speaker turn with maximum overlap with this segment
            best_speaker = None
            best_overlap = 0

            for turn_start, turn_end, speaker_label in speaker_turns:
                # Calculate overlap
                overlap_start = max(seg_start, turn_start)
                overlap_end = min(seg_end, turn_end)
                overlap = max(0, overlap_end - overlap_start)

                if overlap > best_overlap:
                    best_overlap = overlap
                    best_speaker = speaker_label

            # Assign speaker ID
            if best_speaker is None:
                # No speaker turn found, shouldn't happen but handle gracefully
                speaker_id = 1
                confidence = 0.2
            else:
                if best_speaker not in speaker_map:
                    speaker_map[best_speaker] = next_speaker_id
                    next_speaker_id += 1
                speaker_id = speaker_map[best_speaker]
                # Confidence based on overlap percentage
                confidence = min(1.0, best_overlap / (seg_end - seg_start))

            diarized.append(SpeakerSegment(
                speaker_id=speaker_id,
                start_time=seg_start,
                end_time=seg_end,
                text=seg["text"],
                confidence=confidence
            ))

        return diarized

    def _get_audio_duration(self, audio_data: np.ndarray, sample_rate: int) -> float:
        """Get total duration of audio in seconds."""
        return len(audio_data) / sample_rate

    def _build_diarized_transcript(
        self,
        segments: List[SpeakerSegment],
        duration: float,
        conversation_id: str = "temp"
    ) -> DiarizedTranscript:
        """Build the final diarized transcript object."""
        # Count unique speakers
        speaker_ids = set(seg.speaker_id for seg in segments)
        speaker_count = len(speaker_ids)

        # Create default speaker names
        speaker_names = {
            spk_id: f"Speaker {spk_id}"
            for spk_id in speaker_ids
        }

        return DiarizedTranscript(
            conversation_id=conversation_id,
            segments=segments,
            speaker_count=speaker_count,
            speaker_names=speaker_names,
            total_duration=duration,
            created_at=datetime.utcnow()
        )

    def format_transcript(self, diarized: DiarizedTranscript) -> str:
        """
        Format diarized transcript as human-readable text.

        Output format:
        Speaker 1: [00:00-00:05] Hello everyone...
        Speaker 2: [00:05-00:12] Hi there!
        """
        lines = []
        for seg in diarized.segments:
            speaker_name = diarized.speaker_names.get(seg.speaker_id, f"Speaker {seg.speaker_id}")
            timestamp = self._format_timestamp(seg.start_time, seg.end_time)
            confidence_str = f" [{seg.confidence:.1%}]" if seg.confidence < 0.9 else ""
            lines.append(f"{speaker_name}: {timestamp}{confidence_str} {seg.text}")

        return "\n".join(lines)

    @staticmethod
    def _format_timestamp(start: float, end: float) -> str:
        """Format time interval as [MM:SS-MM:SS]."""
        def fmt(t):
            m, s = divmod(int(t), 60)
            return f"{m:02d}:{s:02d}"
        return f"[{fmt(start)}-{fmt(end)}]"

    def get_speaker_stats(self, diarized: DiarizedTranscript) -> Dict[int, Dict[str, Any]]:
        """
        Generate statistics for each speaker.

        Returns: {speaker_id: {name, segment_count, total_time, avg_confidence}}
        """
        stats = {}

        for speaker_id in diarized.speaker_names:
            speaker_segs = [s for s in diarized.segments if s.speaker_id == speaker_id]

            stats[speaker_id] = {
                "name": diarized.speaker_names[speaker_id],
                "segment_count": len(speaker_segs),
                "total_time": sum(s.end_time - s.start_time for s in speaker_segs),
                "avg_confidence": np.mean([s.confidence for s in speaker_segs]) if speaker_segs else 0.0,
                "words": sum(len(s.text.split()) for s in speaker_segs)
            }

        return stats
