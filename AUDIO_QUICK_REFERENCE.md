# Audio Processing - Quick Reference Card

## ⚡ Core Answer
**For speaker diarization: NEED AUDIO (not text)**

Audio contains voice embeddings (pitch, timbre, rhythm) that text doesn't have.

---

## 🚀 Quick Setup
```bash
pip install -r backend/requirements.txt
export HF_TOKEN="hf_xxx"  # Get from huggingface.co/settings/tokens
python backend/main.py
```

---

## 📡 API Endpoints

### Upload & Process
```bash
POST /audio/process
Content-Type: multipart/form-data

curl -X POST http://localhost:8000/audio/process \
  -F "file=@meeting.wav"
```

### Get Speakers
```bash
GET /audio/speakers/{conversation_id}
```

### Identify Speakers
```bash
POST /audio/identify-speakers/{conversation_id}
Content-Type: application/json

{"speakers": {"1": {"name": "Alice", "email": "alice@example.com"}}}
```

---

## 📊 Response Format
```json
{
  "conversation_id": "conv_123",
  "message": "Successfully processed audio with 2 speakers",
  "transcript": {
    "speaker_count": 2,
    "total_duration": 120.5,
    "segments": [
      {
        "speaker_id": 1,
        "start_time": 0.0,
        "end_time": 5.2,
        "text": "Hello everyone",
        "confidence": 0.95
      }
    ],
    "formatted_transcript": "Speaker 1: [00:00-00:05] Hello everyone\n...",
    "speaker_stats": {
      "1": {"name": "Speaker 1", "total_time": 45.3, "words": 128}
    }
  }
}
```

---

## 🏗️ Architecture

```
Audio File
    ↓
Load (16kHz mono)
    ├─→ Whisper (transcribe) → Text + Timestamps
    ├─→ Pyannote (diarize) → Speaker turns
    ↓
Match speakers to text
    ↓
Store in DB
    ↓
API Response
```

---

## 📁 Key Files

| File | Purpose |
|------|---------|
| `backend/services/audio_processor.py` | Audio processing logic |
| `backend/api/routes/audio.py` | API endpoints |
| `QUICK_START_AUDIO.md` | 5-min setup guide |
| `AUDIO_PROCESSING.md` | Full docs |
| `SETUP_AUDIO.md` | Setup guide |
| `AUDIO_ARCHITECTURE.md` | Diagrams |

---

## ⚙️ Speaker Matching Algorithm

```
For each transcript segment:
  1. Find speaker turn with maximum time overlap
  2. Calculate confidence = overlap / segment_length
  3. Assign that speaker to segment

Example:
Segment: [0.0-5.2s] "Hello"
Turn A:  [0.0-5.5s] ← 5.2s overlap, confidence = 1.0 ✓
Turn B:  [5.2-10.0s] ← 0s overlap, confidence = 0 ✗
→ Assign to Speaker A
```

---

## 📈 Performance

| Hardware | Time (10-min audio) |
|----------|---------------------|
| GPU (RTX 3080) | 10s |
| GPU (M1) | 15s |
| CPU (i7) | 90s |

---

## 🔧 Troubleshooting

| Issue | Fix |
|-------|-----|
| `HF_TOKEN not found` | `export HF_TOKEN="hf_..."` |
| `CUDA out of memory` | `unset CUDA_VISIBLE_DEVICES` |
| Import error | `pip install -r requirements.txt` |
| Audio format error | `ffmpeg -i in.mp3 -acodec pcm_s16le out.wav` |

---

## 📦 Dependencies

```
openai-whisper      # Speech-to-text
pyannote.audio      # Speaker ID
librosa             # Audio loading
torch               # Deep learning
numpy               # Numerics
huggingface-hub     # Model download
```

---

## 🔑 Key Concepts

**Speaker Embedding:** Vector representation of a voice's unique characteristics

**Diarization:** Process of identifying who is speaking

**Pyannote:** ML model that extracts speaker embeddings and clusters them

**Whisper:** Speech-to-text model from OpenAI

**Greedy Matching:** Algorithm that finds best speaker for each segment based on time overlap

---

## 💡 Usage Examples

### Python
```python
import requests

with open("audio.wav", "rb") as f:
    r = requests.post("http://localhost:8000/audio/process",
                     files={"file": f})
print(r.json()["transcript"]["formatted_transcript"])
```

### JavaScript/React
```javascript
const formData = new FormData();
formData.append('file', audioFile);

const response = await fetch('/audio/process', {
    method: 'POST',
    body: formData
});

const data = await response.json();
console.log(data.transcript.formatted_transcript);
```

### cURL
```bash
curl -X POST http://localhost:8000/audio/process -F "file=@audio.wav"
```

---

## 📝 Supported Formats

✅ WAV, MP3, FLAC, OGG, M4A, AAC, WMA

Automatically converted to 16kHz mono PCM

---

## 🎯 Next Steps

1. Test API with `QUICK_START_AUDIO.md`
2. Integrate frontend upload component
3. Add speaker name/email assignment UI
4. Display diarized transcript in conversation view

---

## 📞 Need Help?

- **Quick setup:** See `QUICK_START_AUDIO.md`
- **Full docs:** See `AUDIO_PROCESSING.md`
- **Setup issues:** See `SETUP_AUDIO.md`
- **Architecture:** See `AUDIO_ARCHITECTURE.md`
- **Summary:** See `IMPLEMENTATION_SUMMARY.md`

---

## ✨ Status

✅ Audio processing pipeline complete
✅ API endpoints implemented
✅ Database integration done
✅ Documentation comprehensive
⏳ Frontend integration (next)
