# Local Testing Guide - Aperta Audio Processing System

## 📋 Pre-Test Checklist

Before running the system, you need to complete these setup steps:

### 1. Get Required API Keys (⏱️ 5 minutes)

#### Anthropic API Key
- Go to: https://console.anthropic.com
- Click "API keys" in left sidebar
- Create a new key
- Copy and save it securely

#### HuggingFace Token (for Pyannote speaker diarization)
- Go to: https://huggingface.co/settings/tokens
- Click "New token"
- Set name: "aperta-diarization"
- Set role: "read"
- Copy and save it securely

### 2. Update .env File

Edit `backend/.env` and replace the placeholders:

```env
# Replace these with your actual keys:
ANTHROPIC_API_KEY=sk_your_anthropic_key_here
HF_TOKEN=hf_your_huggingface_token_here

# These are already filled in (keep as-is):
SUPABASE_URL=https://sofikamlqpmehintuooj.supabase.co
SUPABASE_KEY=sb_publishable_xBgm2k5VI0Zj6SPid6tpKQ_YXpRzCjN
SUPABASE_DB_PASSWORD=aperta@2026
```

### 3. Install Dependencies (⏱️ 3-5 minutes)

```bash
cd backend
pip install -r requirements.txt
```

This will install:
- Audio processing: `openai-whisper`, `pyannote.audio`
- Database: `asyncpg` (PostgreSQL async driver)
- Storage: `aiofiles`, `boto3`
- And all dependencies

**Note:** On first run, Whisper and Pyannote models will download (~2GB). This takes 2-5 minutes depending on internet speed.

---

## 🧪 Test Phases

### Phase 1: Configuration Validation (1 minute)

Verify that all configuration is loaded correctly:

```bash
cd backend
python3 << 'EOF'
from config import settings
import sys

print("=" * 60)
print("CONFIGURATION VALIDATION")
print("=" * 60)

# Check Supabase
print(f"\n✓ Supabase URL: {settings.supabase_url}")
print(f"✓ Database URL: {settings.database_url[:60]}...")

# Check API Keys
if settings.anthropic_api_key and settings.anthropic_api_key != "your-anthropic-api-key":
    print(f"✓ Anthropic API Key: Set (length: {len(settings.anthropic_api_key)})")
else:
    print("✗ Anthropic API Key: NOT SET - Update .env file")
    sys.exit(1)

if settings.hf_token and settings.hf_token != "your-huggingface-token":
    print(f"✓ HuggingFace Token: Set (length: {len(settings.hf_token)})")
else:
    print("✗ HuggingFace Token: NOT SET - Update .env file")
    sys.exit(1)

# Check storage
print(f"\n✓ Max upload size: {settings.max_upload_size_mb}MB")
print(f"✓ CORS origins: {settings.cors_origins}")

print("\n" + "=" * 60)
print("✅ ALL CONFIGURATION VALID")
print("=" * 60)
EOF
```

**Expected output:**
- ✓ All configuration values shown
- ✓ API keys confirmed as set
- ✓ Database URL shows PostgreSQL connection

---

### Phase 2: Backend Startup (2 minutes)

Start the backend server:

```bash
cd backend
python main.py
```

**Expected output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000

✅ INFO: Database tables created successfully
✅ INFO: Audio processor initialized
✅ INFO: Storage service initialized
✅ Backend ready for requests
```

**If you see errors:**
- `ModuleNotFoundError`: Run `pip install -r requirements.txt`
- `ANTHROPIC_API_KEY not found`: Update `.env` file
- `Connection to Supabase refused`: Check Supabase credentials in `.env`
- `Pyannote license error`: Set `HF_TOKEN` environment variable

---

### Phase 3: API Health Check (1 minute)

In a new terminal, check if the server is healthy:

```bash
curl http://localhost:8000/health
```

**Expected response:**
```json
{
  "status": "healthy",
  "database": "connected",
  "storage": "ready"
}
```

---

### Phase 4: Audio Processing Test (3-5 minutes)

#### Option A: Use a Sample Audio File

If you have an audio file:

```bash
curl -X POST http://localhost:8000/audio/process \
  -F "file=@/path/to/your/audio.wav"
```

#### Option B: Generate a Test Audio File

Create a simple test audio using Python:

```bash
python3 << 'EOF'
import numpy as np
import wave

# Create a simple 30-second test audio (two "speakers" with different tones)
sample_rate = 16000
duration = 30  # seconds

# Speaker 1: 200Hz tone for 10 seconds
t1 = np.linspace(0, 10, int(sample_rate * 10), False)
speaker1 = np.sin(2 * np.pi * 200 * t1) * 0.3

# Silence: 5 seconds
silence = np.zeros(int(sample_rate * 5))

# Speaker 2: 300Hz tone for 10 seconds
t2 = np.linspace(0, 10, int(sample_rate * 10), False)
speaker2 = np.sin(2 * np.pi * 300 * t2) * 0.3

# Silence: 5 seconds
silence2 = np.zeros(int(sample_rate * 5))

# Combine
audio = np.concatenate([speaker1, silence, speaker2, silence2])

# Save
with wave.open('test_audio.wav', 'w') as wav_file:
    wav_file.setnchannels(1)
    wav_file.setsampwidth(2)
    wav_file.setframerate(sample_rate)
    audio_int16 = (audio * 32767).astype(np.int16)
    wav_file.writeframes(audio_int16.tobytes())

print("✅ Created test_audio.wav (30 seconds, 2 different tones)")
EOF
```

Then upload it:

```bash
curl -X POST http://localhost:8000/audio/process \
  -F "file=@test_audio.wav"
```

**Expected response:**
```json
{
  "conversation_id": "conv_abc123...",
  "audio_file_path": "./uploads/conv_abc123.wav",
  "transcript_file_path": "./uploads/conv_abc123_transcript.txt",
  "transcript": "Speaker 1: [0.0-10.0s] ...",
  "speaker_stats": {
    "Speaker 1": {"duration": 10.0, "segments": 1},
    "Speaker 2": {"duration": 10.0, "segments": 1}
  }
}
```

---

### Phase 5: Storage Verification (2 minutes)

Check that files were saved:

```bash
# Check local filesystem storage
ls -la uploads/

# You should see:
# - Audio file: conv_*.wav
# - Transcript file: conv_*_transcript.txt
# - Metadata file: conv_*.json
```

---

### Phase 6: Database Verification (2 minutes)

Go to Supabase Dashboard and verify data:

1. Go to: https://supabase.com/dashboard
2. Select your project: "sofikamlqpmehintuooj"
3. Go to: **SQL Editor** (left sidebar)
4. Run this query:

```sql
SELECT id, title, created_at, speaker_count
FROM conversations
ORDER BY created_at DESC
LIMIT 5;
```

**Expected result:**
- Shows your recently uploaded conversation
- Audio file path stored
- Speaker metadata stored

---

### Phase 7: Full Integration Test (optional, 5 minutes)

Test all components together:

```bash
python3 << 'EOF'
import asyncio
import aiohttp
import json
from pathlib import Path

async def test_full_pipeline():
    print("\n" + "="*60)
    print("FULL INTEGRATION TEST")
    print("="*60)

    # 1. Check server health
    print("\n1️⃣  Checking server health...")
    async with aiohttp.ClientSession() as session:
        async with session.get("http://localhost:8000/health") as resp:
            if resp.status == 200:
                print("   ✓ Server is healthy")
            else:
                print("   ✗ Server health check failed")
                return

    # 2. Check if test audio exists
    print("\n2️⃣  Checking for test audio...")
    if not Path("test_audio.wav").exists():
        print("   ✗ test_audio.wav not found")
        print("   Run the audio generation script first")
        return
    print("   ✓ test_audio.wav found")

    # 3. Upload and process audio
    print("\n3️⃣  Processing audio (this may take 30-60 seconds)...")
    with open("test_audio.wav", "rb") as f:
        async with aiohttp.ClientSession() as session:
            form = aiohttp.FormData()
            form.add_field("file", f, filename="test_audio.wav")

            async with session.post(
                "http://localhost:8000/audio/process",
                data=form
            ) as resp:
                if resp.status == 200:
                    result = await resp.json()
                    print("   ✓ Audio processing successful")
                    print(f"   ✓ Conversation ID: {result['conversation_id']}")
                    print(f"   ✓ Audio saved to: {result['audio_file_path']}")
                    print(f"   ✓ Transcript saved to: {result['transcript_file_path']}")
                    print(f"   ✓ Identified {len(result['speaker_stats'])} speakers")
                else:
                    print(f"   ✗ Audio processing failed: {resp.status}")
                    error = await resp.text()
                    print(f"   Error: {error}")

asyncio.run(test_full_pipeline())
EOF
```

---

## ✅ Success Criteria

Your system is working correctly when:

1. ✅ Configuration loads without errors
2. ✅ Backend starts and shows "Database tables created successfully"
3. ✅ Health endpoint responds with status "healthy"
4. ✅ Audio upload returns a conversation_id
5. ✅ Files appear in `./uploads/` directory
6. ✅ Data appears in Supabase dashboard
7. ✅ Speaker diarization identifies multiple speakers (if audio has them)
8. ✅ Speaker statistics are calculated correctly

---

## 🐛 Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'whisper'"

**Solution:**
```bash
cd backend
pip install -r requirements.txt
```

### Issue: "ANTHROPIC_API_KEY not found"

**Solution:**
1. Go to https://console.anthropic.com
2. Create an API key
3. Edit `backend/.env` and set `ANTHROPIC_API_KEY=sk_...`

### Issue: "Pyannote license error"

**Solution:**
1. Go to https://huggingface.co/pyannote/speaker-diarization-3.0
2. Accept the model card
3. Get your token from https://huggingface.co/settings/tokens
4. Edit `backend/.env` and set `HF_TOKEN=hf_...`

### Issue: "Connection to Supabase refused"

**Solution:**
1. Check that Supabase project is active (not paused)
2. Verify credentials in `backend/.env`:
   - `SUPABASE_URL=https://sofikamlqpmehintuooj.supabase.co`
   - `SUPABASE_DB_PASSWORD=aperta@2026`
3. Try resetting database password in Supabase dashboard

### Issue: "Audio processing is very slow"

**Solution:**
- First run downloads models (~2GB) - this is normal
- Subsequent runs should be 10-30 seconds depending on audio length
- On CPU-only: Processing will be slower (1-2 minutes for 10 minutes of audio)
- GPU recommended for production

---

## 📝 Test Report Template

After testing, create a simple report:

```markdown
# Local Testing Report - [Date]

## Configuration
- [ ] Anthropic API Key: Set and valid
- [ ] HuggingFace Token: Set and valid
- [ ] Supabase Credentials: Verified

## Backend Startup
- [ ] Server starts without errors
- [ ] Database tables created
- [ ] No module import errors

## API Endpoints
- [ ] Health check: ✅
- [ ] Audio upload: ✅
- [ ] Get conversation: ✅

## Audio Processing
- [ ] Transcription working
- [ ] Speaker diarization working
- [ ] Files saved to storage

## Database
- [ ] Data appears in Supabase
- [ ] Conversation record created
- [ ] Speaker metadata stored

## Storage
- [ ] Files in ./uploads/ directory
- [ ] JSON metadata files created
- [ ] Transcript files saved

## Issues Found
- None! System is ready for GitHub commit.

## Recommendation
✅ Ready to commit to GitHub
```

---

## 🚀 Next Steps After Testing

Once you've verified everything works locally:

1. **Create a test report** documenting what you tested
2. **Fix any issues** that come up during testing
3. **Commit to GitHub** when everything passes

Then we can move forward with:
- Frontend integration (audio upload UI)
- Advanced features (real-time processing, speaker names, etc.)
- Production deployment

---

Good luck with testing! Let me know if you hit any issues. 🎉
