"""
Example: Audio Processing & Speaker Diarization

This example demonstrates how to use the AudioProcessor to:
1. Load an audio file
2. Transcribe it with Whisper
3. Identify speakers with Pyannote diarization
4. Generate a speaker-labeled transcript

Usage:
    python examples/audio_processing_example.py path/to/audio.wav
"""

import asyncio
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import numpy as np
import librosa
from services.audio_processor import AudioProcessor


async def main(audio_file: str):
    """Process an audio file and print diarized transcript."""

    print(f"\n{'='*80}")
    print(f"Audio Processing Example: Speaker Diarization")
    print(f"{'='*80}")

    # Initialize processor
    print("\n[1] Initializing audio processor...")
    processor = AudioProcessor()
    print("✓ Processor initialized")

    # Load audio file
    print(f"\n[2] Loading audio file: {audio_file}")
    try:
        audio_data, sr = librosa.load(audio_file, sr=16000, mono=True)
        duration = len(audio_data) / sr
        print(f"✓ Loaded: {duration:.1f}s at {sr}Hz ({len(audio_data)} samples)")
    except Exception as e:
        print(f"✗ Error loading audio: {e}")
        return

    # Process audio
    print(f"\n[3] Processing audio (transcription + diarization)...")
    print("   This may take a minute or two depending on audio length and hardware...")

    try:
        diarized = await processor.process_audio_stream(audio_data, sr)
        print(f"✓ Processing complete")
    except Exception as e:
        print(f"✗ Error processing audio: {e}")
        return

    # Display results
    print(f"\n{'='*80}")
    print(f"RESULTS")
    print(f"{'='*80}")

    print(f"\nAudio Duration: {diarized.total_duration:.1f} seconds")
    print(f"Number of Speakers: {diarized.speaker_count}")
    print(f"Number of Segments: {len(diarized.segments)}")

    # Speaker statistics
    print(f"\n{'-'*80}")
    print("SPEAKER STATISTICS")
    print(f"{'-'*80}")

    stats = processor.get_speaker_stats(diarized)
    for speaker_id in sorted(stats.keys()):
        s = stats[speaker_id]
        print(f"\n{s['name']}:")
        print(f"  Segments: {s['segment_count']}")
        print(f"  Speaking Time: {s['total_time']:.1f}s ({100*s['total_time']/diarized.total_duration:.1f}% of total)")
        print(f"  Words: {s['words']}")
        print(f"  Avg Confidence: {s['avg_confidence']:.1%}")

    # Formatted transcript
    print(f"\n{'-'*80}")
    print("FORMATTED TRANSCRIPT")
    print(f"{'-'*80}\n")

    formatted = processor.format_transcript(diarized)
    print(formatted)

    # Detailed segments
    print(f"\n{'-'*80}")
    print("DETAILED SEGMENTS")
    print(f"{'-'*80}\n")

    for i, seg in enumerate(diarized.segments, 1):
        speaker = diarized.speaker_names[seg.speaker_id]
        timestamp = processor._format_timestamp(seg.start_time, seg.end_time)
        confidence = f"[{seg.confidence:.1%}]" if seg.confidence < 0.9 else ""
        print(f"{i}. {speaker} {timestamp} {confidence}")
        print(f"   {seg.text}\n")

    print(f"{'='*80}")
    print(f"Processing complete!")
    print(f"{'='*80}\n")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python examples/audio_processing_example.py <audio_file>")
        print("\nSupported formats: WAV, MP3, FLAC, OGG, M4A, AAC, WMA")
        print("\nExample:")
        print("  python examples/audio_processing_example.py meeting.wav")
        sys.exit(1)

    audio_file = sys.argv[1]

    # Run async processing
    asyncio.run(main(audio_file))
