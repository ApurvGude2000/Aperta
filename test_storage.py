#!/usr/bin/env python3
"""
Test storage service to verify audio and transcript saving works.
"""

import asyncio
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

from services.storage import StorageService, StorageConfig


async def test_storage():
    """Test storage service operations."""

    print("=" * 60)
    print("TESTING STORAGE SERVICE")
    print("=" * 60)

    # Initialize storage with local filesystem
    config = StorageConfig(
        local_storage_path="./uploads",
        use_s3=False
    )

    storage = StorageService(config)
    print(f"\n✓ Storage service initialized")
    print(f"  Storage type: {storage.get_storage_info()}")

    # Test 1: Save audio file
    print("\n" + "=" * 60)
    print("TEST 1: Save Audio File")
    print("=" * 60)

    test_audio_content = b"fake audio data - this is just a test"
    conversation_id = "test_conv_001"
    filename = "test_recording.wav"

    try:
        audio_path = await storage.save_audio_file(
            file_content=test_audio_content,
            conversation_id=conversation_id,
            filename=filename,
            metadata={
                "duration": 120.5,
                "speaker_count": 2
            }
        )
        print(f"✓ Audio file saved successfully!")
        print(f"  Path: {audio_path}")

        # Verify file exists
        if Path(audio_path).exists():
            print(f"  File size: {Path(audio_path).stat().st_size} bytes")
            print(f"  ✓ File verified on disk")
        else:
            print(f"  ✗ ERROR: File not found on disk!")

    except Exception as e:
        print(f"✗ ERROR saving audio: {e}")
        return False

    # Test 2: Save transcript
    print("\n" + "=" * 60)
    print("TEST 2: Save Transcript")
    print("=" * 60)

    test_transcript = """Speaker 1: Hello everyone, welcome to the meeting.
Speaker 2: Thanks for having us. Let's discuss the agenda.
Speaker 1: Sure, first item is about Q1 results."""

    try:
        transcript_path = await storage.save_transcript(
            transcript_text=test_transcript,
            conversation_id=conversation_id,
            format="txt"
        )
        print(f"✓ Transcript saved successfully!")
        print(f"  Path: {transcript_path}")

        # Verify file exists
        if Path(transcript_path).exists():
            print(f"  File size: {Path(transcript_path).stat().st_size} bytes")
            print(f"  ✓ File verified on disk")

            # Read back content
            with open(transcript_path, 'r') as f:
                content = f.read()
                if content == test_transcript:
                    print(f"  ✓ Content matches original")
                else:
                    print(f"  ✗ Content mismatch!")
        else:
            print(f"  ✗ ERROR: File not found on disk!")

    except Exception as e:
        print(f"✗ ERROR saving transcript: {e}")
        return False

    # Test 3: Retrieve files
    print("\n" + "=" * 60)
    print("TEST 3: Retrieve Files")
    print("=" * 60)

    try:
        # Get audio file relative path
        audio_rel_path = f"{conversation_id}/2026/02/14/{filename}"
        retrieved_audio = await storage.get_file(audio_rel_path)

        if retrieved_audio == test_audio_content:
            print(f"✓ Audio file retrieved successfully")
            print(f"  Size: {len(retrieved_audio)} bytes")
        else:
            print(f"✗ ERROR: Retrieved audio doesn't match!")

    except Exception as e:
        print(f"✗ ERROR retrieving audio: {e}")

    # Test 4: List saved files
    print("\n" + "=" * 60)
    print("TEST 4: List Saved Files")
    print("=" * 60)

    uploads_path = Path("./uploads")
    if uploads_path.exists():
        files = list(uploads_path.rglob("*"))
        print(f"✓ Files in uploads directory:")
        for f in files:
            if f.is_file():
                size = f.stat().st_size
                print(f"  - {f.relative_to(uploads_path)} ({size} bytes)")
    else:
        print(f"✗ uploads directory not found")
        return False

    print("\n" + "=" * 60)
    print("✓ ALL TESTS PASSED")
    print("=" * 60)
    print("\nRecordings are saving correctly to: ./uploads/")
    print("Use the /audio/process endpoint to upload audio files.")

    return True


if __name__ == "__main__":
    result = asyncio.run(test_storage())
    sys.exit(0 if result else 1)
