# Audio Processing - Quick Start (5 Minutes)

## TL;DR

You need **AUDIO** (not text) for speaker diarization because the system extracts acoustic features (pitch, timbre, rhythm) from the raw audio to distinguish between speakers.

## Installation (2 minutes)

```bash
# 1. Install dependencies
cd backend
pip install -r requirements.txt

# 2. Set HuggingFace token (required once)
# Get token: https://huggingface.co/settings/tokens
export HF_TOKEN="hf_xxxxxxxxxxxxxxxxxxxxx"

# 3. Start backend
python main.py
```

## Test It (3 minutes)

**Option A: Using curl**
```bash
curl -X POST http://localhost:8000/audio/process \
  -F "file=@path/to/your/audio.wav"
```

**Option B: Using Python**
```python
import requests

with open("path/to/audio.wav", "rb") as f:
    response = requests.post(
        "http://localhost:8000/audio/process",
        files={"file": f}
    )

# Output contains:
# - speaker_count: number of speakers identified
# - segments: [speaker_id, start_time, end_time, text, confidence]
# - formatted_transcript: human-readable output
print(response.json())
```

**Option C: Using example script**
```bash
python backend/examples/audio_processing_example.py /path/to/audio.wav
```

## What You Get Back

```json
{
    "conversation_id": "conv_abc123",
    "message": "Successfully processed audio with 2 speakers",
    "transcript": {
        "speaker_count": 2,
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

## Add Speaker Names

After processing, identify speakers:

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

## Core Files

| File | Purpose |
|------|---------|
| `backend/services/audio_processor.py` | Speech-to-text + speaker identification |
| `backend/api/routes/audio.py` | API endpoints for audio upload |
| `AUDIO_PROCESSING.md` | Complete technical documentation |
| `SETUP_AUDIO.md` | Detailed setup guide |

## Key Concepts

### Data Flow
```
Audio File → Load (16kHz mono) → Whisper (transcription) → Text + Timestamps
                              ↓
                        Pyannote (embeddings) → Speaker turns
                              ↓
                     Match speakers to text (overlap algorithm)
                              ↓
                        Diarized transcript
```

### Why Greedy Matching?
```
Transcript: "Hello" [0.0-5.2s]
Speaker A:           [0.0-5.5s] ← 100% overlap = assign to A
Speaker B:           [5.2-10.0s] ← 0% overlap = don't assign

Confidence = 5.2 / 5.2 = 1.0 (perfect match)
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `HF_TOKEN not found` | `export HF_TOKEN="hf_..."` |
| `CUDA out of memory` | Use CPU: `unset CUDA_VISIBLE_DEVICES` |
| `Audio format error` | Convert with ffmpeg: `ffmpeg -i in.mp3 -acodec pcm_s16le -ar 16000 out.wav` |
| `ModuleNotFoundError` | `pip install -r requirements.txt` |

## Performance

**Processing time for 10-minute conversation:**
- **GPU (RTX 3080):** ~10 seconds
- **GPU (Apple M1):** ~15 seconds
- **CPU (Intel i7):** ~90 seconds

## Next: Frontend Integration

1. Create upload component in React
2. Send audio to `POST /audio/process`
3. Display formatted transcript
4. Allow speaker identification with `POST /audio/identify-speakers/`

Example:
```javascript
const formData = new FormData();
formData.append('file', audioFile);

const response = await fetch('/audio/process', {
    method: 'POST',
    body: formData
});

const result = await response.json();
console.log(result.transcript.formatted_transcript);
```

## Learn More

- **Full documentation:** See `AUDIO_PROCESSING.md`
- **Setup guide:** See `SETUP_AUDIO.md`
- **Code example:** Run `backend/examples/audio_processing_example.py`
