# Audio System Setup Guide

Quick start guide for setting up the audio recording and transcription system.

## Prerequisites

- Python 3.10+
- Node.js 16+ (for frontend)
- Xcode 14+ (for iOS)
- Git

## Backend Setup

### 1. Install Dependencies

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Create `.env` file in `backend/` directory:

```bash
# Required: API Keys
ANTHROPIC_API_KEY=sk-ant-xxx...            # Get from https://console.anthropic.com
HF_TOKEN=hf_xxxxxx                         # Get from https://huggingface.co/settings/tokens

# Optional: Storage (defaults to local filesystem)
S3_BUCKET_NAME=networkai-transcripts
AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
S3_REGION=us-east-1

# Optional: Database (defaults to SQLite)
DATABASE_URL=sqlite+aiosqlite:///./aperta.db
# OR PostgreSQL/Supabase
# DATABASE_URL=postgresql+asyncpg://user:password@host:5432/db
```

### 3. Get Required API Keys

#### Anthropic API Key
1. Go to https://console.anthropic.com
2. Sign up or log in
3. Create a new API key in your account settings
4. Copy the key to `ANTHROPIC_API_KEY` in `.env`

#### HuggingFace Token
1. Go to https://huggingface.co/settings/tokens
2. Create a new access token (read-only is fine)
3. Accept the license for `pyannote/speaker-diarization-3.0`:
   - Visit https://huggingface.co/pyannote/speaker-diarization-3.0
   - Click "Agree and access repository"
4. Copy the token to `HF_TOKEN` in `.env`

### 4. Initialize Database

```bash
# Alembic migrations (if applicable)
alembic upgrade head

# Or let SQLAlchemy create tables on first run
python -c "from db.session import init_db; init_db()"
```

### 5. Start Backend

```bash
# Development mode (auto-reload)
python main.py

# Or with uvicorn directly
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Check that backend is running:
```bash
curl http://localhost:8000/health
# Should return: {"status": "healthy", "version": "0.1.0"}
```

## Frontend Setup

### 1. Install Dependencies

```bash
cd frontend
npm install
```

### 2. Configure API URL

Edit `frontend/src/api/client.ts`:

```typescript
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
```

Or set environment variable:
```bash
export REACT_APP_API_URL=http://localhost:8000
```

### 3. Start Frontend

```bash
npm run dev
```

Frontend will be available at: http://localhost:5173

## iOS Setup

### 1. Open Project

```bash
cd ApertaMobile
open Aperta.xcodeproj
```

### 2. Configure Backend URL

Edit `ApertaMobile/Aperta/AudioUploadService.swift`:

```swift
private let baseURL = "http://localhost:8000"  // Change to your backend URL

// Or use environment-based configuration:
private var baseURL: String {
    #if DEBUG
    return "http://localhost:8000"
    #else
    return "https://api.aperta.app"  // Production URL
    #endif
}
```

### 3. Build & Run

1. Select target device/simulator in Xcode
2. Click "Run" button or press Cmd+R
3. App will launch on device/simulator

### 4. Test Audio Upload

1. Open app and create an event
2. Record or select audio file
3. Tap "Upload Audio"
4. Check that upload succeeds and displays conversation ID

## Testing the Full Pipeline

### Test 1: Backend Audio Processing

```bash
# Create test audio file (you can use any .wav or .mp3)
# Or download a sample:
wget https://example.com/sample.wav

# Upload and process
curl -X POST http://localhost:8000/audio/process-event \
  -F "file=@sample.wav" \
  -F "event_name=Test Event" \
  -F "location=Test Location"

# Expected response:
# {
#   "conversation_id": "conv_xxx",
#   "audio_recording": {...},
#   "transcription": {...},
#   "ai_analysis": {...}
# }
```

### Test 2: Frontend Audio Display

1. Start frontend: `npm run dev`
2. Navigate to http://localhost:5173
3. Create new conversation or view existing
4. Audio player and transcription should display (if audio data exists)

### Test 3: iOS Upload

1. Run iOS app in simulator
2. Create event: "Test Event"
3. Tap "Upload Audio" button
4. Select audio file from device
5. Tap "Upload Audio"
6. Check for success message with conversation ID

## Common Issues & Solutions

### Issue: "ModuleNotFoundError: No module named 'torch'"

**Solution:**
```bash
pip install torch torchvision torchaudio
```

### Issue: "HuggingFace token required"

**Solution:**
```bash
export HF_TOKEN="hf_xxxxx"
# Verify it's set:
echo $HF_TOKEN
```

### Issue: "Whisper model not found / downloading"

**Solution:** First run takes 5-10 minutes to download models (~500MB)
- Ensure you have internet connection
- Ensure you have at least 2GB free disk space
- Check backend logs: `tail -f backend.log`

### Issue: iOS upload fails with "Connection refused"

**Solution:**
1. Ensure backend is running: `curl http://localhost:8000/health`
2. Check iOS device can reach backend:
   - On simulator: `localhost` = host machine
   - On physical device: Use your machine's IP (e.g., `http://192.168.1.100:8000`)
3. Update URL in `AudioUploadService.swift`

### Issue: Frontend can't connect to backend

**Solution:**
1. Check backend is running: `curl http://localhost:8000/health`
2. Check CORS settings in `backend/config.py`
3. Ensure frontend API URL is correct in `frontend/src/api/client.ts`

### Issue: Audio files not persisting to S3

**Solution:**
1. Verify AWS credentials in `.env`
2. Check S3 bucket exists and is accessible
3. Verify IAM permissions include `s3:PutObject`, `s3:GetObject`
4. Check backend logs for S3 errors

## Database Inspection

### SQLite (Default)

```bash
# Open database
sqlite3 aperta.db

# View audio recordings
SELECT id, conversation_id, file_format, duration, processing_status FROM audio_recordings;

# View transcriptions
SELECT id, recording_id, speaker_count, sentiment, confidence_score FROM transcriptions;

# Exit
.quit
```

### PostgreSQL

```bash
# Connect to database
psql -h localhost -U postgres -d aperta_db

# View audio recordings
SELECT id, conversation_id, file_format, duration, processing_status FROM audio_recordings;

# View transcriptions
SELECT id, recording_id, speaker_count, sentiment, confidence_score FROM transcriptions;

# Exit
\q
```

## Performance Tuning

### Backend

1. **Use GPU for faster processing:**
   ```bash
   # Check if CUDA is available
   python -c "import torch; print(torch.cuda.is_available())"

   # Set device in audio_processor.py
   device = "cuda" if torch.cuda.is_available() else "cpu"
   ```

2. **Increase worker processes:**
   ```bash
   uvicorn main:app --workers 4 --port 8000
   ```

3. **Enable model caching:**
   Models are cached in `~/.cache/torch/` and `~/.cache/huggingface/`

### Frontend

1. **Build for production:**
   ```bash
   npm run build
   # Serves from dist/ folder
   ```

2. **Enable compression:**
   Use Brotli or gzip compression on server

### iOS

1. **Optimize audio file size before upload:**
   - Use lower bitrate (64-128 kbps)
   - Compress audio before uploading
   - For long recordings, split into chunks

## Deployment

### Backend Deployment (Docker)

```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

ENV ANTHROPIC_API_KEY=xxx
ENV HF_TOKEN=xxx

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```bash
docker build -t aperta-backend .
docker run -p 8000:8000 -e ANTHROPIC_API_KEY=xxx -e HF_TOKEN=xxx aperta-backend
```

### Frontend Deployment (Vercel)

```bash
# Install Vercel CLI
npm install -g vercel

# Deploy
vercel --prod
```

### iOS Deployment (App Store)

1. Set Team ID in Xcode: Project > Signing & Capabilities
2. Create App ID in Apple Developer Console
3. Build archive: Product > Archive
4. Distribute through App Store Connect

## Next Steps

1. ✅ Backend running on http://localhost:8000
2. ✅ Frontend running on http://localhost:5173
3. ✅ iOS app configured
4. **Test audio upload flow end-to-end**
5. **Configure database (PostgreSQL or keep SQLite)**
6. **Set up S3 or keep local storage**
7. **Deploy to production**

## Support

For issues or questions:
- Check logs: `tail -f backend.log`
- Check API docs: http://localhost:8000/docs
- Check browser console: F12 in frontend
- Check Xcode console: View > Debug Area for iOS
