# Audio Processing & Speaker Diarization Pipeline

## Overview

The audio processing pipeline is a critical P1 component that enables Aperta to:
1. **Accept audio files** from users (WAV, MP3, FLAC, etc.)
2. **Transcribe speech-to-text** using OpenAI's Whisper model
3. **Identify speakers** using speaker diarization (pyannote.audio)
4. **Match speakers to transcript** segments
5. **Store diarized conversations** in the database

## Architecture

### Data Flow

```
Audio File Upload
    ↓
Audio Preprocessing (convert to 16kHz mono PCM)
    ↓
Parallel Processing:
    ├─→ Whisper Transcription (text + timestamps)
    └─→ Pyannote Speaker Diarization (speaker embeddings + clustering)
    ↓
Speaker Matching (map speakers to transcript segments)
    ↓
Format & Store (save to database with speaker labels)
    ↓
API Response (diarized transcript with speaker stats)
```

## Answer to Your Core Question: Audio or Text?

**You need AUDIO data for speaker diarization.**

**Why:**
- Speaker diarization extracts **voice embeddings** from raw audio
- These embeddings capture acoustic features unique to each speaker:
  - Pitch and frequency characteristics
  - Voice timbre and quality
  - Speech patterns and rhythm
- Text alone loses all this acoustic information needed to distinguish speakers

**The Pipeline:**
- Audio → Whisper → Text transcript (for readability)
- Audio → Pyannote → Speaker identities (who is speaking)
- Combine both → "Speaker 1: [text]", "Speaker 2: [text]"

## Components

### 1. AudioProcessor Service (`services/audio_processor.py`)

**Main Class:** `AudioProcessor`

Responsibilities:
- Initialize Whisper, Pyannote, and Silero VAD models
- Process audio streams (transcribe + diarize)
- Extract speaker embeddings and perform clustering
- Match speakers to transcript segments
- Generate speaker statistics

**Key Methods:**

```python
async def process_audio_stream(audio_data, sample_rate) -> DiarizedTranscript:
    """
    Complete audio processing pipeline.
    Returns transcript with speaker labels and timestamps.
    """

async def _transcribe_audio(audio_data, sample_rate) -> List[Dict]:
    """
    Whisper transcription with streaming support.
    Returns segments: [{start, end, text, confidence}]
    """

async def _diarize_audio(audio_data, sample_rate, transcript) -> List[SpeakerSegment]:
    """
    Speaker diarization using Pyannote.
    Returns speaker-labeled segments matched to transcript.
    """

def format_transcript(diarized) -> str:
    """
    Human-readable output:
    Speaker 1: [00:00-00:05] Hello everyone...
    Speaker 2: [00:05-00:12] Hi there!
    """
```

**Data Classes:**

```python
@dataclass
class SpeakerSegment:
    speaker_id: int           # 1, 2, 3, ...
    start_time: float         # seconds
    end_time: float           # seconds
    text: str                 # transcribed text
    confidence: float         # 0.0-1.0 (based on time overlap)

@dataclass
class DiarizedTranscript:
    conversation_id: str
    segments: List[SpeakerSegment]
    speaker_count: int
    speaker_names: Dict[int, str]  # {1: "Speaker 1", 2: "Speaker 2"}
    total_duration: float
    created_at: datetime
```

### 2. Audio API Routes (`api/routes/audio.py`)

**Endpoints:**

#### POST `/audio/process`
Upload and process audio file.

**Request:**
```
POST /audio/process
Content-Type: multipart/form-data

file: <audio_file.wav|mp3|flac>
conversation_id: (optional) existing conversation ID to update
```

**Response:**
```json
{
    "conversation_id": "conv_123",
    "message": "Successfully processed audio with 2 speakers",
    "transcript": {
        "conversation_id": "conv_123",
        "speaker_count": 2,
        "speaker_names": {"1": "Speaker 1", "2": "Speaker 2"},
        "total_duration": 120.5,
        "segments": [
            {
                "speaker_id": 1,
                "start_time": 0.0,
                "end_time": 5.2,
                "text": "Hello everyone",
                "confidence": 0.95
            },
            {
                "speaker_id": 2,
                "start_time": 5.2,
                "end_time": 10.8,
                "text": "Hi there!",
                "confidence": 0.88
            }
        ],
        "formatted_transcript": "Speaker 1: [00:00-00:05] Hello everyone\nSpeaker 2: [00:05-00:10] Hi there!",
        "speaker_stats": {
            "1": {
                "name": "Speaker 1",
                "segment_count": 3,
                "total_time": 15.2,
                "avg_confidence": 0.92,
                "words": 42
            },
            "2": {
                "name": "Speaker 2",
                "segment_count": 2,
                "total_time": 8.5,
                "avg_confidence": 0.85,
                "words": 18
            }
        }
    }
}
```

#### GET `/audio/speakers/{conversation_id}`
Get speakers for a conversation.

**Response:**
```json
{
    "conversation_id": "conv_123",
    "speaker_count": 2,
    "speakers": [
        {
            "speaker_id": 1,
            "name": "John Doe",
            "email": "john@example.com",
            "company": "Acme Corp",
            "title": "CEO",
            "consent_status": "granted"
        },
        {
            "speaker_id": 2,
            "name": "Jane Smith",
            "email": "jane@example.com",
            "company": "Tech Inc",
            "title": "CTO",
            "consent_status": "granted"
        }
    ]
}
```

#### POST `/audio/identify-speakers/{conversation_id}`
Manually identify speakers (add names, emails, etc.).

**Request:**
```json
{
    "speakers": {
        "1": {
            "name": "John Doe",
            "email": "john@example.com",
            "company": "Acme Corp",
            "title": "CEO"
        },
        "2": {
            "name": "Jane Smith",
            "email": "jane@example.com",
            "company": "Tech Inc",
            "title": "CTO"
        }
    }
}
```

## Technical Details

### Audio Preprocessing

**Input formats supported:**
- WAV (.wav)
- MP3 (.mp3)
- FLAC (.flac)
- OGG (.ogg)
- M4A (.m4a)
- AAC (.aac)
- WMA (.wma)

**Processing:**
1. Load with `librosa.load()`
2. Resample to 16kHz (standard for ASR models)
3. Convert to mono (speaker diarization requirement)
4. Normalize to float32 in range [-1.0, 1.0]

```python
audio_data, sr = librosa.load(file_path, sr=16000, mono=True)
# audio_data: numpy array, shape (num_samples,)
# sr: 16000
```

### Whisper Transcription

**Model:** `whisper-small` (optimized for mobile/edge)

**Features:**
- Handles multiple languages
- Outputs timestamps for each segment
- Confidence scoring per segment
- Real-time streaming support (process chunks)

**Output:**
```python
{
    "segments": [
        {
            "start": 0.0,
            "end": 5.2,
            "text": "Hello everyone",
            "confidence": 0.95
        },
        ...
    ]
}
```

### Speaker Diarization with Pyannote

**Model:** `pyannote/speaker-diarization-3.0`

**Process:**
1. Extract speaker embeddings from audio
2. Create embedding matrix: `(num_frames, embedding_dim)`
3. Cluster embeddings: identify unique speakers
4. Extract speaker turns: `(start_time, end_time, speaker_label)`

**Speaker Matching Algorithm:**

For each transcript segment:
1. Calculate time overlap with each speaker turn
2. Assign speaker with **maximum time overlap**
3. Calculate confidence: `overlap_duration / segment_duration`

Example:
```
Transcript segment: [0.0 - 5.2s] "Hello everyone"
Speaker turns:
  - Speaker A: [0.0 - 5.5s]  → overlap = 5.2s, confidence = 5.2/5.2 = 1.0
  - Speaker B: [5.2 - 10.0s] → overlap = 0s

Result: Assign to Speaker A with confidence 1.0
```

### Speaker Statistics

For each speaker:
- `segment_count`: number of speech segments
- `total_time`: total speaking time in seconds
- `avg_confidence`: average speaker assignment confidence
- `words`: total word count

## Database Schema

New columns added to support diarization:

**Conversation model:**
- `transcript`: Stores diarized transcript with speaker labels
- `status`: tracks processing state (active, completed, failed)

**Participant model:**
- Represents each speaker in the conversation
- `conversation_id`: links to conversation
- `name`: speaker name (optional)
- `email`, `company`, `title`: speaker metadata
- `consent_status`: privacy/recording consent

## Dependencies

Add to `requirements.txt`:

```
openai-whisper>=20230315
pyannote.audio>=2.1.1
librosa>=0.10.0
numpy>=1.24.0
torch>=2.0.0  # GPU support optional but recommended
huggingface-hub>=0.16.0  # For model downloads
```

**Setup:**

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Accept Pyannote license (required once per account):
   - Visit: https://huggingface.co/pyannote/speaker-diarization-3.0
   - Click "Accept repository"
   - Get your HF token: https://huggingface.co/settings/tokens

3. Set environment variable:
```bash
export HF_TOKEN="hf_xxxxxxxxxxxxxxxxxxxxx"
```

## Usage Examples

### Example 1: Basic Audio Processing

```bash
curl -X POST http://localhost:8000/audio/process \
  -F "file=@meeting.wav"
```

Response:
```json
{
    "conversation_id": "conv_abc123",
    "transcript": {
        "speaker_count": 2,
        "formatted_transcript": "Speaker 1: Hello team\nSpeaker 2: Hi there!",
        ...
    }
}
```

### Example 2: Update Existing Conversation

```bash
curl -X POST http://localhost:8000/audio/process \
  -F "file=@meeting.wav" \
  -F "conversation_id=conv_existing_123"
```

### Example 3: Get Speaker Information

```bash
curl http://localhost:8000/audio/speakers/conv_abc123
```

### Example 4: Identify Speakers

```bash
curl -X POST http://localhost:8000/audio/identify-speakers/conv_abc123 \
  -H "Content-Type: application/json" \
  -d '{
    "speakers": {
      "1": {"name": "Alice Johnson", "email": "alice@company.com", "title": "VP Sales"},
      "2": {"name": "Bob Smith", "email": "bob@company.com", "title": "CEO"}
    }
  }'
```

## Performance Considerations

### Latency

- **Audio loading:** ~0.5s per minute of audio
- **Transcription:** ~0.2s per minute of audio (GPU), ~2s (CPU)
- **Diarization:** ~1-2s per minute of audio
- **Total for 5-min meeting:** ~15-30s (GPU), ~60-90s (CPU)

### Memory Usage

- **Whisper (small):** ~500MB
- **Pyannote:** ~1GB
- **Peak (during processing):** ~2-3GB

### Optimization

**For mobile/edge (limited resources):**
1. Use quantized Whisper model
2. Process audio in chunks
3. Implement real-time streaming (process as audio arrives)
4. Use local embeddings cache for speaker re-identification

## Troubleshooting

**Issue: "Pyannote model not available"**
- Solution: Set HF_TOKEN environment variable and accept license

**Issue: Out of memory during diarization**
- Solution: Process shorter audio clips, or use CPU-optimized settings

**Issue: Poor speaker segmentation**
- Solution:
  - Ensure audio is clear and at proper volume
  - Check for background noise (low SNR)
  - May need manual correction via `/audio/identify-speakers/`

## Future Enhancements

**P2 Priority:**
- Voice activity detection (VAD) to skip silence
- Real-time streaming transcription
- Overlapping speech detection
- Speaker re-identification across conversations

**P3 Priority:**
- Custom speaker vocabulary injection
- Acoustic environment adaptation
- Multi-language support
- Emotional tone detection

**P4 Priority:**
- Federated learning for speaker embeddings
- Privacy-preserving diarization
- Hardware acceleration (GPU/TPU)
