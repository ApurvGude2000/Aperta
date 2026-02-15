#!/bin/bash

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}========================================${NC}"
echo -e "${YELLOW}  Aperta Audio Processing Test Suite${NC}"
echo -e "${YELLOW}========================================${NC}\n"

# Change to backend directory
cd backend

# Test 1: Configuration Validation
echo -e "${YELLOW}[1/5] Configuration Validation...${NC}"
python3 << 'EOF'
try:
    from config import settings
    assert settings.anthropic_api_key
    assert settings.hf_token
    assert settings.supabase_url
    print("✓ Configuration validation passed")
except Exception as e:
    print(f"✗ Configuration validation failed: {e}")
    exit(1)
EOF

if [ $? -ne 0 ]; then
    echo -e "${RED}Configuration validation failed${NC}"
    exit 1
fi

# Test 2: Audio Processor Initialization
echo -e "\n${YELLOW}[2/5] Audio Processor Initialization...${NC}"
python3 << 'EOF'
try:
    from services.audio_processor import AudioProcessor
    processor = AudioProcessor()
    print("✓ Audio processor initialized")
except Exception as e:
    print(f"✗ Audio processor initialization failed: {e}")
    exit(1)
EOF

if [ $? -ne 0 ]; then
    echo -e "${RED}Audio processor initialization failed${NC}"
    exit 1
fi

# Test 3: Storage Service Initialization
echo -e "\n${YELLOW}[3/5] Storage Service Initialization...${NC}"
python3 << 'EOF'
try:
    from services.storage import StorageService
    from config import settings
    storage = StorageService(settings)
    info = storage.get_storage_info()
    print(f"✓ Storage service initialized ({info['storage_type']} backend)")
except Exception as e:
    print(f"✗ Storage service initialization failed: {e}")
    exit(1)
EOF

if [ $? -ne 0 ]; then
    echo -e "${RED}Storage service initialization failed${NC}"
    exit 1
fi

# Test 4: Test Audio File Generation
echo -e "\n${YELLOW}[4/5] Generating Test Audio File...${NC}"
python3 << 'EOF'
import numpy as np
import wave

# Create a simple 10-second test audio (two "speakers" with different tones)
sample_rate = 16000
duration = 10  # seconds

# Speaker 1: 200Hz tone for 3 seconds
t1 = np.linspace(0, 3, int(sample_rate * 3), False)
speaker1 = np.sin(2 * np.pi * 200 * t1) * 0.3

# Silence: 2 seconds
silence = np.zeros(int(sample_rate * 2))

# Speaker 2: 300Hz tone for 3 seconds
t2 = np.linspace(0, 3, int(sample_rate * 3), False)
speaker2 = np.sin(2 * np.pi * 300 * t2) * 0.3

# Silence: 2 seconds
silence2 = np.zeros(int(sample_rate * 2))

# Combine
audio = np.concatenate([speaker1, silence, speaker2, silence2])

# Save
with wave.open('test_audio.wav', 'w') as wav_file:
    wav_file.setnchannels(1)
    wav_file.setsampwidth(2)
    wav_file.setframerate(sample_rate)
    audio_int16 = (audio * 32767).astype(np.int16)
    wav_file.writeframes(audio_int16.tobytes())

print("✓ Test audio file generated (10 seconds, 2 speakers)")
EOF

if [ $? -ne 0 ]; then
    echo -e "${RED}Test audio generation failed${NC}"
    exit 1
fi

# Test 5: Audio Processing
echo -e "\n${YELLOW}[5/5] Testing Audio Processing Pipeline...${NC}"
echo -e "Note: This may take 30-60 seconds on first run (models download)"
python3 << 'EOF'
import asyncio
from services.audio_processor import AudioProcessor

async def test_audio_processing():
    processor = AudioProcessor()
    try:
        result = await processor.process_audio_stream("test_audio.wav")
        print(f"✓ Audio processing successful")
        # Result is a DiarizedTranscript object
        print(f"  - Conversation ID: {result.conversation_id}")
        print(f"  - Speakers detected: {result.speaker_count}")
        print(f"  - Transcript segments: {len(result.segments)}")
        print(f"  - Total duration: {result.total_duration:.1f}s")
        return True
    except Exception as e:
        print(f"✗ Audio processing failed: {e}")
        import traceback
        traceback.print_exc()
        return False

success = asyncio.run(test_audio_processing())
exit(0 if success else 1)
EOF

if [ $? -ne 0 ]; then
    echo -e "${RED}Audio processing test failed${NC}"
    exit 1
fi

# All tests passed
echo -e "\n${GREEN}========================================${NC}"
echo -e "${GREEN}  ✅ ALL TESTS PASSED${NC}"
echo -e "${GREEN}========================================${NC}"
echo -e "\nYour system is ready for local testing!"
echo -e "Run: ${YELLOW}python main.py${NC} to start the server"
echo -e "Then: ${YELLOW}curl -X POST http://localhost:8000/audio/process -F 'file=@test_audio.wav'${NC}"
