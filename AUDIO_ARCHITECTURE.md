# Audio Processing Architecture Diagrams

## High-Level Data Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                      Frontend (React)                            │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ Audio Recording Component                               │   │
│  │ - Record audio from microphone (future)                │   │
│  │ - OR upload existing audio file                        │   │
│  └───────────────────┬─────────────────────────────────────┘   │
└────────────────────┼──────────────────────────────────────────┘
                     │ Audio file (WAV, MP3, FLAC, etc.)
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│               Backend API - FastAPI                             │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ POST /audio/process                                     │   │
│  │ - Receive audio file                                   │   │
│  │ - Validate format                                      │   │
│  │ - Call AudioProcessor                                 │   │
│  └───────────────────┬─────────────────────────────────────┘   │
└────────────────────┼──────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│            AudioProcessor Service (ML Pipeline)                 │
│                                                                  │
│  ┌────────────────────┐         ┌─────────────────────┐        │
│  │  Audio Loading     │         │ Preprocessing       │        │
│  │  (librosa)         │────────▶│ - 16kHz mono PCM   │        │
│  │  - Load any format │         │ - Normalize [-1,1] │        │
│  │  - Convert to numpy│         └────────┬────────────┘        │
│  └────────────────────┘                  │                     │
│                                          ▼                     │
│          ┌──────────────────────────────────────────┐          │
│          │   PARALLEL PROCESSING (Async)            │          │
│          └────┬───────────────────────────┬─────────┘          │
│               │                           │                    │
│         ┌─────▼──────┐            ┌──────▼────────┐           │
│         │  Whisper   │            │   Pyannote    │           │
│         │(Transcribe)│            │ (Diarization) │           │
│         │            │            │               │           │
│         │ - Extract  │            │ - Extract     │           │
│         │   text     │            │   embeddings  │           │
│         │ - Timestamps│           │ - Cluster     │           │
│         │ - Confidence│           │   speakers    │           │
│         └─────┬──────┘            └──────┬────────┘           │
│               │                          │                    │
│         ┌─────▼──────────────────────────▼────┐               │
│         │  Speaker Matching Algorithm        │               │
│         │  - For each transcript segment:   │               │
│         │    - Find max overlap speaker turn│               │
│         │    - Calculate confidence         │               │
│         │    - Assign speaker ID            │               │
│         └─────┬──────────────────────────────┘               │
│               │                                              │
│         ┌─────▼──────────────────┐                          │
│         │  DiarizedTranscript    │                          │
│         │  - segments[]          │                          │
│         │  - speaker_count       │                          │
│         │  - speaker_names{}     │                          │
│         │  - speaker_stats{}     │                          │
│         └─────┬──────────────────┘                          │
└──────────────┼─────────────────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Database (SQLite/PostgreSQL)                 │
│  ┌─────────────────┐  ┌──────────────┐  ┌──────────────────┐   │
│  │ Conversations   │  │ Participants │  │ Entities/Actions │   │
│  │ - id (PK)       │  │ - id (PK)    │  │ - Extracted from │   │
│  │ - transcript    │  │ - name       │  │   conversation   │   │
│  │ - status        │  │ - email      │  │ - speaker linked │   │
│  │ - participants  │  │ - company    │  │                  │   │
│  │ - entities      │  │ - title      │  │                  │   │
│  │ - action_items  │  │ - consent    │  │                  │   │
│  └─────────────────┘  │ - lead_score │  │                  │   │
│                       └──────────────┘  └──────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

## AudioProcessor Internal Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                    AudioProcessor Class                       │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│  Models (loaded on init):                                   │
│  ├─ whisper_model: OpenAI Whisper (small)                  │
│  ├─ diarization_model: Pyannote Speaker Diarization 3.0    │
│  └─ vad_model: Silero Voice Activity Detection              │
│                                                               │
│  Main Methods:                                              │
│  ├─ process_audio_stream(audio, sr)                        │
│  │  └─ Orchestrates full pipeline                          │
│  │                                                          │
│  ├─ _transcribe_audio(audio, sr)                           │
│  │  ├─ Runs Whisper.transcribe()                           │
│  │  ├─ Extracts segments with timestamps                   │
│  │  └─ Returns: List[{start, end, text, confidence}]       │
│  │                                                          │
│  ├─ _diarize_audio(audio, sr, transcripts)                 │
│  │  ├─ Runs Pyannote diarization                           │
│  │  ├─ Extracts speaker turns                              │
│  │  ├─ Matches speakers to transcript segments             │
│  │  └─ Returns: List[SpeakerSegment]                       │
│  │                                                          │
│  ├─ format_transcript(diarized)                            │
│  │  └─ Returns human-readable speaker-labeled text         │
│  │                                                          │
│  └─ get_speaker_stats(diarized)                            │
│     └─ Returns Dict[speaker_id, stats]                     │
│                                                               │
└──────────────────────────────────────────────────────────────┘
```

## Speaker Matching Algorithm Detail

```
Input: Transcript segments + Speaker turns

Transcript Segments:
  Segment 1: [0.0-5.2s] "Hello everyone"
  Segment 2: [5.2-10.8s] "How are you?"
  Segment 3: [10.8-15.3s] "I'm doing great"

Speaker Turns (from Pyannote):
  Turn A: [0.0-5.5s] Speaker A
  Turn B: [5.2-10.0s] Speaker B
  Turn C: [10.0-15.3s] Speaker A

Process:
┌─ Segment 1: [0.0-5.2s]
│  └─ Check overlap with each turn:
│     ├─ Turn A [0.0-5.5s]: overlap = 5.2 ✓ (max)
│     ├─ Turn B [5.2-10.0s]: overlap = 0
│     └─ Turn C [10.0-15.3s]: overlap = 0
│  └─ Assign to Speaker A, confidence = 5.2/5.2 = 1.00
│
├─ Segment 2: [5.2-10.8s]
│  └─ Check overlap with each turn:
│     ├─ Turn A [0.0-5.5s]: overlap = 0
│     ├─ Turn B [5.2-10.0s]: overlap = 4.8 ✓ (max)
│     └─ Turn C [10.0-15.3s]: overlap = 0.8
│  └─ Assign to Speaker B, confidence = 4.8/5.6 = 0.86
│
└─ Segment 3: [10.8-15.3s]
   └─ Check overlap with each turn:
      ├─ Turn A [0.0-5.5s]: overlap = 0
      ├─ Turn B [5.2-10.0s]: overlap = 0
      └─ Turn C [10.0-15.3s]: overlap = 4.5 ✓ (max)
   └─ Assign to Speaker A, confidence = 4.5/4.5 = 1.00

Output:
  Speaker 1 (A): [0.0-5.2s] "Hello everyone" [conf: 1.00]
  Speaker 2 (B): [5.2-10.8s] "How are you?" [conf: 0.86]
  Speaker 1 (A): [10.8-15.3s] "I'm doing great" [conf: 1.00]
```

## API Request/Response Flow

```
HTTP Request
│
├─ POST /audio/process
│  ├─ Headers: Content-Type: multipart/form-data
│  ├─ Body: file (audio file), conversation_id (optional)
│  │
│  ▼
│  ┌──────────────────────────────────────┐
│  │ FastAPI Route Handler               │
│  │ 1. Validate file format             │
│  │ 2. Load audio with librosa          │
│  │ 3. Call processor.process_audio_stream()
│  │ 4. Save to database                 │
│  │ 5. Build response                   │
│  └──────────────────────────────────────┘
│  │
│  ▼
HTTP Response (200 OK)
│
└─ {
    "conversation_id": "conv_abc123",
    "message": "Successfully processed audio with 2 speakers",
    "transcript": {
      "conversation_id": "conv_abc123",
      "speaker_count": 2,
      "segments": [
        {
          "speaker_id": 1,
          "start_time": 0.0,
          "end_time": 5.2,
          "text": "Hello everyone",
          "confidence": 0.95
        },
        ...
      ],
      "speaker_names": {"1": "Speaker 1", "2": "Speaker 2"},
      "formatted_transcript": "Speaker 1: [00:00-00:05] Hello everyone\n...",
      "speaker_stats": {
        "1": {
          "name": "Speaker 1",
          "segment_count": 5,
          "total_time": 45.3,
          "avg_confidence": 0.92,
          "words": 128
        },
        ...
      }
    }
  }
```

## Database Schema

```
┌─────────────────────────────────────────────────────────────┐
│              conversations                                   │
├─────────────────────────────────────────────────────────────┤
│ id (PK)         │ user_id    │ title     │ transcript        │
│ "conv_123"      │ "user_1"   │ "Meeting" │ "Speaker 1: Hi"   │
│                 │            │           │                   │
│ status          │ recording_url │ location │ created_at       │
│ "completed"     │ "/path/..."   │ "NYC"    │ 2024-01-15       │
└─────────────────────────────────────────────────────────────┘
         │
         │ 1:N relationship (one conversation, many participants)
         │
         ▼
┌─────────────────────────────────────────────────────────────┐
│              participants                                    │
├─────────────────────────────────────────────────────────────┤
│ id (PK)         │ conversation_id │ name          │ email    │
│ "part_1"        │ "conv_123"      │ "Alice Johns" │ "a@...
"  │
│ "part_2"        │ "conv_123"      │ "Bob Smith"   │ "b@...
"  │
│                 │                 │               │         │
│ company         │ title  │ consent_status │ lead_score │    │
│ "Acme Corp"     │ "VP"   │ "granted"      │ 0.85       │    │
│ "Tech Inc"      │ "CEO"  │ "granted"      │ 0.92       │    │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│              entities                                        │
├─────────────────────────────────────────────────────────────┤
│ id (PK)    │ conversation_id │ type     │ value    │ confidence
│ "ent_1"    │ "conv_123"      │ "person" │ "Alice"  │ 0.98
│ "ent_2"    │ "conv_123"      │ "company"│ "Acme"   │ 0.95
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│              action_items                                    │
├─────────────────────────────────────────────────────────────┤
│ id (PK)    │ conversation_id │ description │ responsible_party
│ "act_1"    │ "conv_123"      │ "Send..."   │ "Alice"
│ "act_2"    │ "conv_123"      │ "Schedule..." │ "Bob"
└─────────────────────────────────────────────────────────────┘
```

## Model Loading & Memory

```
┌────────────────────────────────────────────────────────────────┐
│                       AudioProcessor.__init__()                │
├────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. Detect device:                                            │
│     cuda_available? → "cuda" : "cpu"                          │
│                                                                 │
│  2. Load Whisper:                                             │
│     whisper.load_model("small") → 500MB, 1.5GB RAM           │
│                                                                 │
│  3. Load Pyannote:                                            │
│     Pipeline.from_pretrained("pyannote/...") → 1GB, 1GB RAM   │
│                                                                 │
│  4. Load Silero VAD:                                          │
│     load_silero_vad() → 50MB, 0.3GB RAM                      │
│                                                                 │
│  Memory Usage During Processing:                             │
│  ├─ Audio buffer: ~500MB (typical 10-min conversation)       │
│  ├─ Whisper processing: +1GB                                 │
│  ├─ Pyannote embedding: +1GB                                 │
│  └─ Total peak: ~3.5GB                                       │
│                                                                 │
│  Optimization:                                               │
│  ├─ Models cached after first load                           │
│  ├─ Can process multiple files without reloading             │
│  └─ FP16 precision on GPU for smaller memory footprint       │
│                                                                 │
└────────────────────────────────────────────────────────────────┘
```

## Error Handling Flow

```
Audio Upload
    │
    ├─ File validation
    │  └─ Invalid format? → 400 Bad Request
    │
    ├─ Audio loading
    │  ├─ Corrupted file? → 400 Bad Request
    │  └─ librosa error? → 400 Bad Request
    │
    ├─ Transcription
    │  ├─ GPU OOM? → Fallback to CPU (slower)
    │  └─ Model error? → 500 Server Error
    │
    ├─ Diarization
    │  ├─ HF token missing? → Warning, fallback to single speaker
    │  ├─ GPU OOM? → Fallback to CPU
    │  └─ Model error? → Warning, use simple diarization
    │
    ├─ Database save
    │  └─ DB error? → 500 Server Error
    │
    └─ Success → 200 OK with transcript
```
