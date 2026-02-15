# Aperta - Ready to Run! 🚀

Everything is configured locally. Here's how to start testing.

---

## ✅ What's Ready

- ✅ **Audio Processing** - Transcription + Speaker Diarization
- ✅ **File Storage** - Local filesystem + optional S3
- ✅ **Supabase Database** - PostgreSQL cloud database
- ✅ **API Endpoints** - All configured and ready
- ✅ **Configuration** - Automatic from environment variables

---

## 🚀 Quick Start (3 Steps)

### Step 1: Install Dependencies
```bash
cd /Users/harshimsaluja/Documents/GitHub/Aperta
pip install -r backend/requirements.txt
```

This installs:
- Audio processing (Whisper, Pyannote)
- Database drivers (asyncpg for PostgreSQL)
- File storage (aiofiles, boto3)
- And all other dependencies

### Step 2: Set API Keys
```bash
export ANTHROPIC_API_KEY="your-api-key"
export HF_TOKEN="hf_your-token"
```

Get them from:
- **Anthropic API Key**: https://console.anthropic.com
- **HuggingFace Token**: https://huggingface.co/settings/tokens

### Step 3: Start Backend
```bash
cd backend
python main.py
```

You should see:
```
✅ INFO: Uvicorn running on http://0.0.0.0:8000
✅ INFO: Database tables created successfully
✅ INFO: Audio processor initialized
```

**That's it!** Your backend is running with Supabase PostgreSQL! 🎉

---

## 🧪 Test It

Upload audio:
```bash
curl -X POST http://localhost:8000/audio/process \
  -F "file=@test_audio.wav"
```

Response will include:
- `conversation_id` - Database record ID
- `audio_file_path` - Where audio was saved
- `transcript_file_path` - Where transcript was saved
- `transcript` - Diarized transcript with speaker labels
- `speaker_stats` - Statistics per speaker

---

## 📊 View Your Data

Go to **Supabase Dashboard**:
1. https://supabase.com/dashboard
2. Select your project "sofikamlqpmehintuooj"
3. Go to **SQL Editor** (left sidebar)
4. Run queries:

```sql
-- See all conversations
SELECT id, title, created_at FROM conversations;

-- See speakers
SELECT c.title, p.name, p.email
FROM conversations c
JOIN participants p ON c.id = p.conversation_id;

-- See action items
SELECT description, responsible_party FROM action_items;
```

---

## 🔐 Configuration Details

Your `.env` file contains:

```env
SUPABASE_URL=https://sofikamlqpmehintuooj.supabase.co
SUPABASE_KEY=sb_publishable_xBgm2k5VI0Zj6SPid6tpKQ_YXpRzCjN
SUPABASE_DB_PASSWORD=aperta@2026
```

The backend automatically:
1. Reads these credentials
2. Builds the PostgreSQL connection string
3. Connects to Supabase
4. Creates all tables

**Never commit .env to Git** - it's already in .gitignore!

---

## 📈 Data Flow

```
Upload Audio
    ↓
Transcribe (Whisper)
    ↓
Identify Speakers (Pyannote)
    ↓
Save Files:
├─ Audio → ./uploads/ (or S3)
├─ Transcript → ./uploads/ (or S3)
└─ Metadata → JSON file
    ↓
Save to Supabase:
├─ Conversation record
├─ Participants (speakers)
├─ Entities (companies, topics)
├─ Action items (commitments)
└─ Privacy logs
    ↓
Return Response
├─ conversation_id
├─ audio_file_path
├─ transcript_file_path
└─ Speaker statistics
```

---

## 🔧 Optional: S3 Cloud Storage

To save audio/transcripts to AWS S3 instead of local:

```env
AWS_ACCESS_KEY_ID=your-key
AWS_SECRET_ACCESS_KEY=your-secret
S3_BUCKET_NAME=aperta-audio
S3_REGION=us-east-1
```

Without this, files save to `./uploads/` locally (perfectly fine for development).

---

## 📚 API Endpoints

### Audio Processing
- `POST /audio/process` - Upload and process audio
- `GET /audio/storage-info` - Check storage status
- `GET /audio/speakers/{id}` - Get speakers for conversation
- `POST /audio/identify-speakers/{id}` - Assign names to speakers

### Conversation Management
- `GET /conversations` - List all conversations
- `GET /conversations/{id}` - Get conversation details
- `POST /conversations` - Create new conversation
- `PUT /conversations/{id}` - Update conversation
- `DELETE /conversations/{id}` - Delete conversation
- `POST /conversations/{id}/analyze` - Analyze with AI agents

### Q&A
- `POST /qa` - Ask questions about conversations
- `GET /qa/sessions/{id}` - Get Q&A session

---

## 🧠 What's Happening Behind the Scenes

1. **Audio Upload**
   - Validates file format
   - Loads with librosa (16kHz mono)
   - Ready for processing

2. **Parallel Processing**
   - Whisper transcribes audio → text with timestamps
   - Pyannote extracts speaker embeddings → speaker clustering
   - Greedy matching algorithm assigns speakers to transcript segments

3. **Storage**
   - Audio file saved (async, non-blocking)
   - Transcript saved (async, non-blocking)
   - Metadata tracked (duration, speaker count, etc.)

4. **Database**
   - Conversation record created
   - Speaker records created
   - All linked and queryable

5. **Response**
   - Returns file paths and diarized transcript
   - Speaker statistics included
   - Conversation ID for future queries

---

## 🐛 Troubleshooting

### Error: "ModuleNotFoundError"
**Solution:** Run `pip install -r backend/requirements.txt`

### Error: "ANTHROPIC_API_KEY not found"
**Solution:** `export ANTHROPIC_API_KEY="your-key"`

### Error: "Connection to Supabase refused"
**Solution:** Check your `.env` file has correct credentials

### Error: "Pyannote license error"
**Solution:** Get HuggingFace token and set `export HF_TOKEN="hf_xxx"`

### Files not saving?
**Check:** `ls -la uploads/` - should have files there

### Data not appearing in Supabase?
**Check:** Go to Supabase dashboard → SQL Editor → run `SELECT * FROM conversations;`

---

## 📋 Checklist

Before testing:
- [ ] Dependencies installed (`pip install -r backend/requirements.txt`)
- [ ] ANTHROPIC_API_KEY set
- [ ] HF_TOKEN set
- [ ] .env file exists in backend/ directory

When testing:
- [ ] Backend starts successfully
- [ ] Can upload audio file
- [ ] Response includes conversation_id
- [ ] Files appear in ./uploads/
- [ ] Data appears in Supabase dashboard

---

## 🎯 Next Steps

1. **Get API Keys** (5 minutes)
   - Anthropic: https://console.anthropic.com
   - HuggingFace: https://huggingface.co/settings/tokens

2. **Install & Run** (2 minutes)
   ```bash
   pip install -r backend/requirements.txt
   cd backend
   export ANTHROPIC_API_KEY="..."
   export HF_TOKEN="..."
   python main.py
   ```

3. **Test Upload** (1 minute)
   ```bash
   curl -X POST http://localhost:8000/audio/process -F "file=@audio.wav"
   ```

4. **View Results** (1 minute)
   - Check Supabase dashboard
   - Query your data

**Total Time: ~10 minutes to full system running!** ⏱️

---

## ✨ Summary

You now have a **complete AI audio processing system** with:
- Real-time transcription
- Speaker identification
- Cloud database
- File persistence
- Full API

All configured and ready to run locally. Once you get the API keys, you're good to go! 🚀

---

## 📞 Need Help?

See:
- `SUPABASE_SETUP.md` - Supabase configuration details
- `AUDIO_PROCESSING.md` - Audio processing details
- `STORAGE_GUIDE.md` - File storage options
- `STORAGE_IMPLEMENTATION.md` - Storage technical details

Good luck! 🎉
