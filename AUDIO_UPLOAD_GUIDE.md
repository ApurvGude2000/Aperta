# Audio Upload & Saving Guide

## Status: ✅ WORKING

Audio files are **now being saved correctly** to `./uploads/` directory with the following structure:

```
./uploads/
└── {conversation_id}/
    └── {YYYY}/{MM}/{DD}/
        ├── {filename}.wav (audio file)
        ├── {filename}_metadata.json (metadata)
        └── {conversation_id}_transcript.txt (transcript)
```

## How It Works

### 1. Upload Audio File

```bash
curl -X POST "http://localhost:8000/audio/process" \
  -F "file=@/path/to/your/audio.wav"
```

**Supported formats:** WAV, MP3, FLAC, OGG, M4A, AAC, WMA

### 2. Response Example

```json
{
  "conversation_id": "conv_a1b2c3d4e5f6",
  "transcript": {
    "conversation_id": "conv_a1b2c3d4e5f6",
    "segments": [
      {
        "speaker_id": 1,
        "start_time": 0.0,
        "end_time": 5.2,
        "text": "Hello everyone, welcome to the meeting.",
        "confidence": 0.95
      },
      {
        "speaker_id": 2,
        "start_time": 5.3,
        "end_time": 8.1,
        "text": "Thanks for having me here.",
        "confidence": 0.92
      }
    ],
    "speaker_count": 2,
    "speaker_names": {
      "1": "Speaker 1",
      "2": "Speaker 2"
    },
    "total_duration": 120.5,
    "formatted_transcript": "Speaker 1: Hello everyone, welcome to the meeting.\nSpeaker 2: Thanks for having me here.",
    "speaker_stats": {
      "1": {
        "speaking_time": 45.2,
        "word_count": 150,
        "segments_count": 5
      },
      "2": {
        "speaking_time": 30.1,
        "word_count": 95,
        "segments_count": 3
      }
    },
    "created_at": "2026-02-15T00:00:00"
  },
  "audio_file_path": "uploads/conv_a1b2c3d4e5f6/2026/02/15/audio.wav",
  "transcript_file_path": "uploads/conv_a1b2c3d4e5f6/2026/02/15/conv_a1b2c3d4e5f6_transcript.txt",
  "message": "Successfully processed audio with 2 speakers and saved to storage"
}
```

### 3. Where Files Are Saved

- **Audio files:** `./uploads/{conversation_id}/{YYYY}/{MM}/{DD}/{filename}`
- **Transcripts:** `./uploads/{conversation_id}/{YYYY}/{MM}/{DD}/{conversation_id}_transcript.txt`
- **Metadata:** `./uploads/{conversation_id}/{YYYY}/{MM}/{DD}/{filename}_metadata.json`

### 4. Check Storage Info

```bash
curl http://localhost:8000/audio/storage-info
```

Response:
```json
{
  "storage_type": "local",
  "local_path": "./uploads",
  "s3_bucket": null,
  "s3_enabled": false
}
```

## What Gets Saved

### Audio File
- Original uploaded audio file
- Automatically converted to 16kHz mono PCM internally
- Stored as-is in original format (WAV, MP3, etc.)

### Metadata JSON
```json
{
  "duration": 120.5,
  "speaker_count": 2,
  "uploaded_at": "2026-02-15T12:34:56.789123"
}
```

### Transcript File
Plain text format:
```
Speaker 1: Hello everyone, welcome to the meeting.
Speaker 2: Thanks for having me here.
Speaker 1: Let's discuss the Q1 results.
```

## Supported Audio Formats

✅ WAV
✅ MP3
✅ FLAC
✅ OGG
✅ M4A
✅ AAC
✅ WMA

## API Endpoints

### Process Audio (Main Endpoint)
```
POST /audio/process
```
Upload an audio file for transcription and speaker diarization

### Get Storage Info
```
GET /audio/storage-info
```
Get current storage configuration

### Get Speakers for Conversation
```
GET /audio/speakers/{conversation_id}
```
Get identified speakers in a conversation

### Identify Speakers (Manual)
```
POST /audio/identify-speakers/{conversation_id}
```
Manually assign names to speakers

## Upload Examples

### Using Python
```python
import requests

# Upload audio file
with open('recording.wav', 'rb') as f:
    response = requests.post(
        'http://localhost:8000/audio/process',
        files={'file': f}
    )

result = response.json()
print(f"Conversation ID: {result['conversation_id']}")
print(f"Audio saved to: {result['audio_file_path']}")
print(f"Transcript saved to: {result['transcript_file_path']}")
```

### Using JavaScript/Node.js
```javascript
const FormData = require('form-data');
const fs = require('fs');
const axios = require('axios');

async function uploadAudio() {
  const formData = new FormData();
  formData.append('file', fs.createReadStream('recording.wav'));

  const response = await axios.post(
    'http://localhost:8000/audio/process',
    formData,
    { headers: formData.getHeaders() }
  );

  console.log('Conversation ID:', response.data.conversation_id);
  console.log('Audio saved to:', response.data.audio_file_path);
  console.log('Transcript saved to:', response.data.transcript_file_path);
}

uploadAudio();
```

### Using Postman
1. Open Postman
2. Create a **POST** request to `http://localhost:8000/audio/process`
3. Go to **Body** tab
4. Select **form-data**
5. Add key: `file`, Type: **File**
6. Browse and select your audio file
7. Click **Send**

## Database Storage

In addition to filesystem storage, conversations are also saved to Supabase PostgreSQL with:
- Conversation ID
- Transcript text
- Recording URL (audio_file_path)
- Participants (speakers)
- Conversation status

## S3 Support (Optional)

To enable AWS S3 storage, set these environment variables:

```bash
export AWS_ACCESS_KEY_ID="your-access-key"
export AWS_SECRET_ACCESS_KEY="your-secret-key"
export S3_BUCKET_NAME="your-bucket"
export S3_REGION="us-east-1"
```

The system will automatically detect S3 credentials and use S3 instead of local storage.

## Troubleshooting

### Issue: "uploads directory not found"
**Solution:** The directory is created automatically on first upload, or manually:
```bash
mkdir -p ./uploads
```

### Issue: "Permission denied"
**Solution:** Ensure write permissions:
```bash
chmod 755 ./uploads
```

### Issue: Files not appearing
**Solution:** Check server logs:
```bash
# Check if server is running
curl http://localhost:8000/audio/storage-info

# Check uploads directory
ls -la ./uploads/
```

### Issue: Upload fails with "Invalid file format"
**Solution:** Only these formats are supported:
- WAV, MP3, FLAC, OGG, M4A, AAC, WMA

## Quick Test

Run the test script:
```bash
python test_storage.py
```

This will verify:
- ✓ Storage service initialization
- ✓ Audio file saving
- ✓ Transcript saving
- ✓ File retrieval
- ✓ Directory structure

## Summary

✅ **Audio files are being saved to:** `./uploads/`
✅ **Transcripts are being saved to:** `./uploads/{conv_id}/{date}/`
✅ **Database integration:** Files also indexed in Supabase
✅ **S3 support:** Optional cloud storage available

**All recording functionality is operational!**
