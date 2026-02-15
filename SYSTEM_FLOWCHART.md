# 🔄 Complete System Flowchart

## What Happens When You Push to GitHub and Run

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                               │
│                    YOU PUSH TO GITHUB                                         │
│                    git push origin main                                       │
│                                                                               │
└─────────────────────────┬───────────────────────────────────────────────────┘
                          │
                          ▼
        ┌─────────────────────────────────────┐
        │  GitHub Repository Updated          │
        │  • Code pushed to main branch        │
        │  • Commit: c25a60f visible          │
        │  • Ready for other developers       │
        └────────────┬────────────────────────┘
                     │
                     ▼
        ┌─────────────────────────────────────┐
        │  YOU START THE BACKEND              │
        │  $ python backend/main.py           │
        └────────────┬────────────────────────┘
                     │
                     ▼
╔═════════════════════════════════════════════════════════════════════════════╗
║                     BACKEND STARTUP SEQUENCE                                ║
╠═════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║  1. Load Configuration (backend/config.py)                                  ║
║     ├─ Load .env file (override=True)                                       ║
║     ├─ Read Anthropic API Key                                               ║
║     ├─ Read HuggingFace Token                                               ║
║     ├─ Read Supabase credentials                                            ║
║     └─ AUTO-BUILD PostgreSQL connection string from Supabase               ║
║        Example: postgresql+asyncpg://postgres:password@db.xxx.supabase.co  ║
║                                                                              ║
║  2. Initialize Audio Processing (backend/services/audio_processor.py)       ║
║     ├─ Load Whisper model (speech-to-text)                                  ║
║     ├─ Load Pyannote model (speaker diarization)                            ║
║     ├─ Load Silero VAD (voice activity detection)                           ║
║     └─ Ready for audio processing requests                                  ║
║                                                                              ║
║  3. Initialize Storage Service (backend/services/storage.py)                ║
║     ├─ Check for S3 credentials (optional)                                  ║
║     ├─ If AWS credentials present: Use S3                                   ║
║     ├─ Else: Use local filesystem (./uploads)                               ║
║     └─ Create storage directories if needed                                 ║
║                                                                              ║
║  4. Connect to Database (Supabase PostgreSQL)                               ║
║     ├─ Create async connection pool (asyncpg)                               ║
║     ├─ Auto-create tables on first run:                                     ║
║     │  ├─ conversations table (stores audio metadata)                       ║
║     │  ├─ participants table (identifies speakers)                          ║
║     │  ├─ transcripts table (stores text output)                            ║
║     │  └─ entities & action_items tables                                    ║
║     └─ Verify connection to Supabase                                        ║
║                                                                              ║
║  5. Initialize FastAPI Server                                              ║
║     ├─ Register API routes                                                  ║
║     ├─ Configure CORS (localhost:5173, localhost:3000)                     ║
║     ├─ Enable file uploads (multipart/form-data)                            ║
║     └─ Start Uvicorn server at http://0.0.0.0:8000                          ║
║                                                                              ║
║  ✅ Server Ready! Listening for requests...                                 ║
║                                                                              ║
╚═════════════════════════════════════════════════════════════════════════════╝
                     │
                     ▼
        ┌─────────────────────────────────────┐
        │  SERVER RUNNING                     │
        │  http://localhost:8000              │
        │  Ready for audio uploads            │
        └────────────┬────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                      USER UPLOADS AUDIO FILE                                 │
│                  POST /audio/process                                         │
│              with audio file (WAV, MP3, M4A, OGG, FLAC)                      │
└─────────────────────┬───────────────────────────────────────────────────────┘
                      │
                      ▼
╔═════════════════════════════════════════════════════════════════════════════╗
║                    AUDIO PROCESSING PIPELINE                                ║
╠═════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║  STEP 1: Receive & Validate File                                            ║
║  ├─ Check file size (< 100MB)                                               ║
║  ├─ Check file format (MP3, WAV, M4A, OGG, FLAC)                            ║
║  └─ Generate unique conversation_id (e.g., "conv_abc123def456")            ║
║                                                                              ║
║  STEP 2: Store Original Audio File                                          ║
║  ├─ Save to: ./uploads/conv_abc123def456.wav (or original format)           ║
║  ├─ Generate metadata JSON                                                  ║
║  └─ Store location for future reference                                     ║
║                                                                              ║
║  STEP 3: Process Audio in Parallel (Async)                                  ║
║  │                                                                           ║
║  ├─ Path A: TRANSCRIPTION (Whisper)                                         ║
║  │  ├─ Convert audio to 16kHz mono PCM                                      ║
║  │  ├─ Run through OpenAI Whisper model                                     ║
║  │  ├─ Output: Text with timestamps                                         ║
║  │  └─ Example:                                                             ║
║  │     [0.0-5.2s] "Hello everyone, welcome to our meeting"                 ║
║  │     [5.2-10.1s] "Let's discuss the project plan"                        ║
║  │                                                                           ║
║  └─ Path B: SPEAKER DIARIZATION (Pyannote)                                  ║
║     ├─ Extract voice embeddings from audio                                  ║
║     ├─ Cluster similar voices (speaker identification)                      ║
║     ├─ Output: Speaker turns with confidence scores                         ║
║     └─ Example:                                                             ║
║        Speaker_0: [0.0-5.2s] confidence: 0.95                              ║
║        Speaker_1: [5.2-10.1s] confidence: 0.92                             ║
║                                                                              ║
║  STEP 4: Match Speakers to Transcript (Greedy Algorithm)                    ║
║  ├─ For each transcript segment:                                            ║
║  │  ├─ Find speaker turn with maximum time overlap                          ║
║  │  └─ Calculate confidence = overlap_duration / segment_duration           ║
║  │                                                                           ║
║  └─ Result: Diarized transcript                                             ║
║     Example:                                                                ║
║     Speaker 1 [0.0-5.2s]: "Hello everyone, welcome to our meeting"         ║
║     Speaker 2 [5.2-10.1s]: "Let's discuss the project plan"               ║
║                                                                              ║
║  STEP 5: Generate Output Transcript                                         ║
║  ├─ Format human-readable transcript                                        ║
║  ├─ Save to: ./uploads/conv_abc123def456_transcript.txt                    ║
║  └─ Content:                                                                ║
║     [Speaker 1, 0:00-0:05] "Hello everyone, welcome to our meeting"       ║
║     [Speaker 2, 0:05-0:10] "Let's discuss the project plan"               ║
║                                                                              ║
╚═════════════════════════════════════════════════════════════════════════════╝
                      │
                      ▼
╔═════════════════════════════════════════════════════════════════════════════╗
║                    STORE DATA (3 Places)                                    ║
╠═════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║  STORAGE LOCATION 1: Local Filesystem (./uploads)                           ║
║  ├─ conv_abc123def456.wav                                                   ║
║  │  └─ Original audio file                                                  ║
║  ├─ conv_abc123def456_transcript.txt                                        ║
║  │  └─ Human-readable diarized transcript                                   ║
║  └─ conv_abc123def456.json                                                  ║
║     └─ Metadata (speakers, confidence, duration, timestamps)                ║
║                                                                              ║
║  STORAGE LOCATION 2: Supabase PostgreSQL Database                           ║
║  ├─ Table: conversations                                                    ║
║  │  ├─ id: "conv_abc123def456"                                              ║
║  │  ├─ title: (optional user title)                                         ║
║  │  ├─ audio_file_path: "./uploads/conv_abc123def456.wav"                  ║
║  │  ├─ transcript_file_path: "./uploads/conv_abc123def456_transcript.txt"  ║
║  │  ├─ speaker_count: 2                                                     ║
║  │  ├─ total_duration: 10.1                                                 ║
║  │  ├─ created_at: 2026-02-14T20:30:45.123Z                                 ║
║  │  └─ updated_at: 2026-02-14T20:30:45.123Z                                 ║
║  │                                                                           ║
║  ├─ Table: participants                                                     ║
║  │  ├─ id: 1                                                                ║
║  │  ├─ conversation_id: "conv_abc123def456"                                 ║
║  │  ├─ speaker_id: 0                                                        ║
║  │  ├─ name: (optional - "John", "Sarah", etc.)                            ║
║  │  ├─ confidence: 0.95                                                     ║
║  │  └─ speaking_duration: 5.2 (seconds)                                     ║
║  │                                                                           ║
║  ├─ Table: segments (transcript segments)                                   ║
║  │  ├─ id: 1                                                                ║
║  │  ├─ conversation_id: "conv_abc123def456"                                 ║
║  │  ├─ speaker_id: 0                                                        ║
║  │  ├─ start_time: 0.0                                                      ║
║  │  ├─ end_time: 5.2                                                        ║
║  │  ├─ text: "Hello everyone, welcome to our meeting"                      ║
║  │  └─ confidence: 0.95                                                     ║
║  │                                                                           ║
║  └─ Tables: entities, action_items                                          ║
║     └─ (Created for future extraction of key information)                   ║
║                                                                              ║
║  STORAGE LOCATION 3 (Optional): AWS S3                                      ║
║  ├─ If AWS credentials set in .env:                                         ║
║  │  ├─ Bucket: aperta-audio                                                 ║
║  │  ├─ Path: conv_abc123def456/audio.wav                                    ║
║  │  ├─ Path: conv_abc123def456/transcript.txt                               ║
║  │  └─ Path: conv_abc123def456/metadata.json                                ║
║  └─ Else: Uses local filesystem (fallback)                                  ║
║                                                                              ║
╚═════════════════════════════════════════════════════════════════════════════╝
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                    RETURN API RESPONSE                                       │
│                                                                              │
│  HTTP 200 OK                                                                │
│  {                                                                          │
│    "conversation_id": "conv_abc123def456",                                 │
│    "audio_file_path": "./uploads/conv_abc123def456.wav",                  │
│    "transcript_file_path": "./uploads/conv_abc123def456_transcript.txt",  │
│    "transcript": "Speaker 1 [0:00-0:05] Hello everyone...",              │
│    "speaker_stats": {                                                      │
│      "Speaker 1": {"duration": 5.2, "segments": 1, "confidence": 0.95},  │
│      "Speaker 2": {"duration": 4.9, "segments": 1, "confidence": 0.92}   │
│    },                                                                      │
│    "total_duration": 10.1,                                                │
│    "speaker_count": 2,                                                    │
│    "created_at": "2026-02-14T20:30:45.123Z"                              │
│  }                                                                          │
└─────────────────────────────────────────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                    FRONTEND RECEIVES DATA                                    │
│                                                                              │
│  1. Show transcript with speaker labels                                    │
│     [Speaker 1] "Hello everyone, welcome to our meeting"                  │
│     [Speaker 2] "Let's discuss the project plan"                          │
│                                                                              │
│  2. Display speaker statistics                                              │
│     Speaker 1: 5.2 seconds (52%)                                           │
│     Speaker 2: 4.9 seconds (48%)                                           │
│                                                                              │
│  3. Let user manage speakers (assign names, edit, etc.)                    │
│     Speaker 1 → "John Smith"                                              │
│     Speaker 2 → "Sarah Johnson"                                            │
│                                                                              │
│  4. Download transcript as text file (optional)                             │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Data Flow Summary

### Where Data Goes

```
User uploads WAV file
        │
        ├──→ Saved to: ./uploads/conv_abc123.wav
        │
        ├──→ Processed by Whisper (transcription)
        │    └──→ Output: Text with timestamps
        │
        ├──→ Processed by Pyannote (diarization)
        │    └──→ Output: Speaker turns
        │
        ├──→ Saved to: ./uploads/conv_abc123_transcript.txt
        │
        ├──→ Saved to: ./uploads/conv_abc123.json (metadata)
        │
        ├──→ Stored in Supabase PostgreSQL
        │    ├─ conversations table
        │    ├─ participants table
        │    ├─ segments table
        │    └─ entities, action_items tables
        │
        ├──→ (Optional) Saved to AWS S3
        │
        └──→ Returned to Frontend via API Response
             └──→ Display to User
```

---

## Database Schema (What's Stored in Supabase)

```sql
-- conversations table
CREATE TABLE conversations (
  id VARCHAR PRIMARY KEY,           -- "conv_abc123def456"
  title VARCHAR,                    -- optional user title
  audio_file_path VARCHAR,          -- "./uploads/conv_abc123def456.wav"
  transcript_file_path VARCHAR,     -- "./uploads/conv_abc123def456_transcript.txt"
  speaker_count INT,                -- 2
  total_duration FLOAT,             -- 10.1 seconds
  created_at TIMESTAMP,             -- when uploaded
  updated_at TIMESTAMP              -- last modified
);

-- participants (speakers) table
CREATE TABLE participants (
  id SERIAL PRIMARY KEY,
  conversation_id VARCHAR,          -- "conv_abc123def456"
  speaker_id INT,                   -- 0, 1, 2, etc.
  name VARCHAR,                     -- optional: "John", "Sarah"
  confidence FLOAT,                 -- 0.95
  speaking_duration FLOAT           -- 5.2 seconds
);

-- segments (transcript) table
CREATE TABLE segments (
  id SERIAL PRIMARY KEY,
  conversation_id VARCHAR,          -- "conv_abc123def456"
  speaker_id INT,                   -- 0, 1, etc.
  start_time FLOAT,                 -- 0.0
  end_time FLOAT,                   -- 5.2
  text VARCHAR,                     -- "Hello everyone..."
  confidence FLOAT                  -- 0.95
);

-- entities table (for future use)
CREATE TABLE entities (
  id SERIAL PRIMARY KEY,
  conversation_id VARCHAR,
  entity_text VARCHAR,              -- "John Smith"
  entity_type VARCHAR,              -- "PERSON", "COMPANY", etc.
  mentioned_by_speaker INT
);

-- action_items table (for future use)
CREATE TABLE action_items (
  id SERIAL PRIMARY KEY,
  conversation_id VARCHAR,
  item_text VARCHAR,                -- "Follow up with customer"
  assigned_to INT,                  -- speaker_id
  status VARCHAR                    -- "PENDING", "COMPLETED"
);
```

---

## File Storage Layout

```
./uploads/
├── conv_abc123def456.wav
│   └─ Original audio file (can be large - 10MB+)
│
├── conv_abc123def456_transcript.txt
│   └─ Human-readable transcript
│      [Speaker 1, 0:00-0:05] "Hello everyone..."
│      [Speaker 2, 0:05-0:10] "Let's discuss..."
│
├── conv_abc123def456.json
│   └─ Metadata file
│      {
│        "conversation_id": "conv_abc123def456",
│        "speaker_count": 2,
│        "total_duration": 10.1,
│        "speakers": [
│          {"id": 0, "confidence": 0.95, "duration": 5.2},
│          {"id": 1, "confidence": 0.92, "duration": 4.9}
│        ],
│        "segments": [...]
│      }
│
├── conv_def789...
├── conv_ghi123...
└── ... (one directory per uploaded audio file)
```

---

## Complete Request/Response Example

### Request
```bash
curl -X POST http://localhost:8000/audio/process \
  -F "file=@meeting.wav"
```

### Response
```json
{
  "conversation_id": "conv_a1b2c3d4e5f6",
  "audio_file_path": "./uploads/conv_a1b2c3d4e5f6.wav",
  "transcript_file_path": "./uploads/conv_a1b2c3d4e5f6_transcript.txt",
  "transcript": "Speaker 1 [0:00-0:05] Hello everyone, welcome to our meeting\nSpeaker 2 [0:05-0:10] Let's discuss the project plan",
  "speaker_stats": {
    "Speaker 1": {
      "duration": 5.2,
      "segments": 1,
      "confidence": 0.95
    },
    "Speaker 2": {
      "duration": 4.9,
      "segments": 1,
      "confidence": 0.92
    }
  },
  "total_duration": 10.1,
  "speaker_count": 2,
  "created_at": "2026-02-14T20:30:45.123000+00:00"
}
```

---

## What Gets Stored - Summary Table

| What | Where | Why | Size |
|------|-------|-----|------|
| Original Audio File | `./uploads/*.wav` | Reference, future re-processing | 5-100MB+ |
| Transcript Text | `./uploads/*_transcript.txt` | User reads, downloads, shares | 10-100KB |
| Metadata JSON | `./uploads/*.json` | Timestamps, confidence scores | 5-50KB |
| Conversation Info | Supabase `conversations` | Database queries, organize | 1KB |
| Speaker Info | Supabase `participants` | Who spoke, confidence | 1KB per speaker |
| Transcript Segments | Supabase `segments` | Search, analyze, extract entities | 10-100KB |
| Entities (Future) | Supabase `entities` | Name extraction, PII detection | Variable |
| Action Items (Future) | Supabase `action_items` | Task tracking | Variable |
| Optional: S3 Backup | AWS S3 | Cloud backup, redundancy | Same as local |

---

## Timeline Example

```
User uploads 10-minute meeting recording

Time 0s:    Upload received
Time 1s:    Audio file saved to ./uploads/
Time 2-45s: Whisper transcription (GPU: ~5s, CPU: ~30s)
Time 45-90s: Pyannote speaker diarization (GPU: ~10s, CPU: ~40s)
Time 90s:   Matching speakers to transcript (instant)
Time 91s:   Save to database (Supabase)
Time 92s:   Return response to frontend
            → User sees transcript with speaker labels immediately

TOTAL: ~90 seconds end-to-end (faster with GPU)
```

---

## Security & Privacy

```
What happens to your data:

✅ Audio File
   • Stored locally in ./uploads/ (or S3 if configured)
   • NOT sent to external AI services
   • Stays under your control

✅ Transcription
   • Done locally using Whisper model
   • Model downloaded once, runs locally
   • Text never sent externally

✅ Speaker Diarization
   • Done locally using Pyannote model
   • Voice embeddings generated locally
   • Never leaves your server

✅ Database
   • Supabase PostgreSQL in your account
   • You control access and retention
   • Can delete anytime

✅ API Keys
   • Stored in .env (not in code)
   • Protected by .gitignore
   • Not committed to GitHub
```

This is everything that happens in your system! 🎉
