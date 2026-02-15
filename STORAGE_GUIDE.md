# Audio Storage & Persistence Guide

## Overview

The audio processing pipeline now includes a complete **storage layer** that handles:

1. **Audio file persistence** - Save uploaded audio files
2. **Transcript persistence** - Save diarized transcripts
3. **Metadata storage** - Track audio metadata and speaker info
4. **Database integration** - Store conversation records and speaker data
5. **Multi-backend support** - Local filesystem or AWS S3

---

## Architecture

```
Audio Upload
    ↓
Process (transcribe + diarize)
    ↓
┌─────────────────────────────────────────────┐
│         Save to Storage (Parallel)           │
│  ├─ Audio File → Local FS or S3             │
│  ├─ Transcript → Local FS or S3             │
│  └─ Metadata → JSON + Database              │
└─────────────────────────────────────────────┘
    ↓
Save to Database
    ├─ Conversation record
    ├─ Participants (speakers)
    ├─ Entities (extracted)
    └─ Action items
    ↓
Return Response with File Paths
```

---

## Storage Backends

### Local Filesystem (Default - Development)

Files saved to: `./uploads/`

Structure:
```
uploads/
├── conv_abc123/
│   ├── 2024/01/15/
│   │   ├── meeting.wav
│   │   ├── meeting_metadata.json
│   │   └── conv_abc123_transcript.txt
│   ├── 2024/01/16/
│   │   ├── presentation.mp3
│   │   └── ...
```

**Setup:**
No configuration needed. Files automatically saved to `./uploads/` directory.

**Pros:**
- Easy to set up for development
- No credentials needed
- Fast local access
- Files directly accessible

**Cons:**
- Not suitable for production
- Limited scalability
- No automatic backup

### AWS S3 (Production)

Files saved to: `s3://bucket-name/audio/` and `s3://bucket-name/transcripts/`

**Setup:**

1. Create S3 bucket:
```bash
aws s3api create-bucket --bucket aperta-audio --region us-east-1
```

2. Set environment variables:
```bash
export AWS_ACCESS_KEY_ID="your-access-key"
export AWS_SECRET_ACCESS_KEY="your-secret-key"
export S3_BUCKET_NAME="aperta-audio"
export S3_REGION="us-east-1"
```

3. Or add to `.env`:
```env
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
S3_BUCKET_NAME=aperta-audio
S3_REGION=us-east-1
```

**Pros:**
- Production-ready
- Highly scalable
- Built-in redundancy
- Automatic backups
- Access from anywhere

**Cons:**
- Requires AWS account and credentials
- Costs per request/storage
- Network latency

### S3-Compatible Services (Wasabi, MinIO, R2)

Works with any S3-compatible service.

**Setup for Cloudflare R2:**

```bash
export AWS_ACCESS_KEY_ID="your-r2-access-key"
export AWS_SECRET_ACCESS_KEY="your-r2-secret-key"
export S3_BUCKET_NAME="aperta-audio"
export S3_ENDPOINT_URL="https://xxxxx.r2.cloudflarestorage.com"
```

---

## Storage Service API

### StorageConfig

Configuration for storage backend:

```python
from services.storage import StorageConfig, StorageService

config = StorageConfig(
    local_storage_path="./uploads",
    use_s3=True,
    s3_bucket="aperta-audio",
    s3_region="us-east-1",
    s3_access_key="your-key",
    s3_secret_key="your-secret",
    s3_endpoint_url="optional-endpoint-url",
)

storage = StorageService(config)
```

### Save Audio File

```python
audio_path = await storage.save_audio_file(
    file_content=audio_bytes,
    conversation_id="conv_123",
    filename="meeting.wav",
    metadata={
        "duration": 120.5,
        "speaker_count": 2,
        "uploaded_at": "2024-01-15T10:30:00"
    }
)
```

Returns: Path or S3 URL where file was saved

**Local:** `./uploads/conv_123/2024/01/15/meeting.wav`
**S3:** `s3://bucket/audio/conv_123/2024/01/15/meeting.wav`

### Save Transcript

```python
transcript_path = await storage.save_transcript(
    transcript_text="Speaker 1: Hello\nSpeaker 2: Hi...",
    conversation_id="conv_123",
    format="txt"  # or "json", "md", etc.
)
```

Returns: Path or S3 URL where transcript was saved

### Retrieve File

```python
content = await storage.get_file("conv_123/2024/01/15/meeting.wav")
if content:
    # Process file
    pass
```

### Delete File

```python
success = await storage.delete_file("conv_123/2024/01/15/meeting.wav")
```

### Get Storage Info

```python
info = storage.get_storage_info()
# Returns:
# {
#     "storage_type": "s3" or "local",
#     "local_path": "./uploads",
#     "s3_bucket": "aperta-audio",
#     "s3_enabled": true
# }
```

---

## API Endpoints

### POST /audio/process

Upload audio, process, and save to storage.

**Request:**
```bash
curl -X POST http://localhost:8000/audio/process \
  -F "file=@meeting.wav"
```

**Response:**
```json
{
  "conversation_id": "conv_abc123",
  "audio_file_path": "./uploads/conv_abc123/2024/01/15/meeting.wav",
  "transcript_file_path": "./uploads/conv_abc123/2024/01/15/conv_abc123_transcript.txt",
  "transcript": {
    "speaker_count": 2,
    "segments": [...],
    "formatted_transcript": "Speaker 1: Hello...",
    "speaker_stats": {...}
  },
  "message": "Successfully processed audio with 2 speakers and saved to storage"
}
```

### GET /audio/storage-info

Get current storage configuration.

**Request:**
```bash
curl http://localhost:8000/audio/storage-info
```

**Response:**
```json
{
  "storage_type": "local",
  "local_path": "./uploads",
  "s3_bucket": null,
  "s3_enabled": false
}
```

---

## Data Organization

### Directory Structure (Local)

```
uploads/
├── conv_xyz/                    # Conversation ID
│   ├── 2024/01/15/
│   │   ├── meeting.wav          # Audio file
│   │   ├── meeting_metadata.json  # Audio metadata
│   │   └── conv_xyz_transcript.txt  # Transcript
│   └── 2024/01/16/
│       └── ...
├── conv_abc/
│   └── ...
```

### Database Records

**Conversations table:**
- `id` - Conversation ID
- `transcript` - Diarized transcript text
- `recording_url` - Path to saved audio file
- `status` - "completed", "processing", etc.
- `created_at`, `updated_at` - Timestamps

**Participants table:**
- `id` - Participant ID
- `conversation_id` - Link to conversation
- `name` - Speaker name
- `email`, `company`, `title` - Speaker info
- `consent_status` - Recording consent status

---

## Metadata Storage

### Audio File Metadata

When saving audio, metadata is attached:

**Local storage:** Saved as `filename_metadata.json`
```json
{
  "duration": 120.5,
  "speaker_count": 2,
  "uploaded_at": "2024-01-15T10:30:00",
  "filename": "meeting.wav"
}
```

**S3 storage:** Saved as S3 object metadata (queryable via API)

### Transcript Metadata

Stored alongside transcript:
- `timestamp` - When transcript was created
- `speaker_count` - Number of speakers
- `total_duration` - Audio duration
- `conversation_id` - Reference to conversation

---

## Cost Optimization

### Local Storage
- ✅ Free (filesystem storage)
- No bandwidth costs
- Best for development/testing

### S3
- **Estimated costs** (rough):
  - `PUT` request: $0.005 per 1,000 requests
  - `GET` request: $0.0004 per 1,000 requests
  - Storage: $0.023 per GB/month (Standard)

**Example:**
- 10 hours of audio per month (6GB)
- 200 upload operations
- 500 download operations

**Cost:** ~$0.15/month + ~$0.14/month storage = ~$0.29/month

### Optimization Tips

1. **Compress transcripts:**
```python
# Save as compressed JSON instead of plain text
import gzip
compressed = gzip.compress(transcript_json.encode())
await storage.save_transcript(compressed, ...)
```

2. **Set S3 lifecycle policies:**
- Delete old recordings after 90 days
- Move to Glacier for long-term storage
- Archive transcripts to cheaper storage

3. **Use S3 Transfer Acceleration:**
```env
S3_ENDPOINT_URL=https://s3-accelerate.amazonaws.com
```

4. **Implement retention policies:**
```python
# Example: Keep audio for 30 days, transcript forever
if age > 30_days:
    await storage.delete_file(audio_path)
```

---

## Security

### Local Storage
- ✅ Files stored locally (secure for development)
- ✅ Access controlled by OS permissions
- ⚠️ No encryption at rest (add if needed)

### S3 Storage
- ✅ Enable server-side encryption:
```bash
aws s3api put-bucket-encryption \
  --bucket aperta-audio \
  --server-side-encryption-configuration '{
    "Rules": [{
      "ApplyServerSideEncryptionByDefault": {
        "SSEAlgorithm": "AES256"
      }
    }]
  }'
```

- ✅ Restrict bucket access:
```bash
# Only allow specific IAM user
aws s3api put-bucket-policy --bucket aperta-audio --policy '{...}'
```

- ✅ Enable versioning:
```bash
aws s3api put-bucket-versioning \
  --bucket aperta-audio \
  --versioning-configuration Status=Enabled
```

- ✅ Use IAM roles instead of access keys
- ✅ Rotate credentials regularly

---

## Monitoring & Debugging

### Check Storage Info

```bash
curl http://localhost:8000/audio/storage-info
```

### View Local Files

```bash
# List all uploaded files
ls -la uploads/

# Check file size
du -sh uploads/conv_*/
```

### Monitor S3 Bucket

```bash
# List objects in bucket
aws s3 ls s3://aperta-audio/ --recursive

# Get bucket size
aws s3api list-objects-v2 \
  --bucket aperta-audio \
  --summarize \
  --human-readable
```

### Check Database

```bash
# Get conversation with file paths
SELECT id, recording_url, transcript FROM conversations LIMIT 5;
```

---

## Troubleshooting

### Issue: Files not saving

**Check storage info endpoint:**
```bash
curl http://localhost:8000/audio/storage-info
```

**Check logs:**
```bash
tail -f backend.log | grep -i storage
```

**Verify permissions:**
```bash
ls -la uploads/
chmod -R 755 uploads/
```

### Issue: S3 authentication failed

**Verify credentials:**
```bash
aws s3 ls --region us-east-1
```

**Check environment variables:**
```bash
echo $AWS_ACCESS_KEY_ID
echo $AWS_SECRET_ACCESS_KEY
```

**Test S3 connection:**
```python
import boto3
s3 = boto3.client('s3')
s3.list_buckets()
```

### Issue: File not found

**Check path format:**
```python
# Correct format: "conversation_id/date/filename"
# Not: "/conversation_id/date/filename"
# Not: "uploads/conversation_id/date/filename"
```

---

## Migration Guide

### Migrate from Local to S3

```python
import os
from pathlib import Path
from services.storage import StorageService, StorageConfig

# Source: Local filesystem
local_config = StorageConfig(local_storage_path="./uploads", use_s3=False)
local_storage = StorageService(local_config)

# Destination: S3
s3_config = StorageConfig(
    use_s3=True,
    s3_bucket="aperta-audio",
    s3_region="us-east-1",
    s3_access_key=os.getenv("AWS_ACCESS_KEY_ID"),
    s3_secret_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
)
s3_storage = StorageService(s3_config)

# Migrate files
for file_path in Path("./uploads").rglob("*"):
    if file_path.is_file():
        content = await local_storage.get_file(str(file_path))
        await s3_storage.s3_client.put_object(
            Bucket=s3_config.s3_bucket,
            Key=f"migrated/{file_path.name}",
            Body=content
        )
```

---

## Next Steps

1. **Choose storage backend** - Use local for development, S3 for production
2. **Configure credentials** - Set environment variables if using S3
3. **Test upload** - Upload audio and verify files are saved
4. **Implement retention** - Delete old files per your retention policy
5. **Monitor costs** - Track S3 expenses if using cloud storage
6. **Backup transcripts** - Consider backing up to separate storage

---

## API Reference

### StorageService Methods

| Method | Purpose |
|--------|---------|
| `save_audio_file()` | Save uploaded audio file |
| `save_transcript()` | Save diarized transcript |
| `get_file()` | Retrieve file content |
| `delete_file()` | Delete file |
| `get_storage_info()` | Get storage configuration |

### Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `local_storage_path` | str | `./uploads` | Local filesystem path |
| `use_s3` | bool | `False` | Enable S3 storage |
| `s3_bucket` | str | `None` | S3 bucket name |
| `s3_region` | str | `us-east-1` | AWS region |
| `s3_access_key` | str | `None` | AWS access key |
| `s3_secret_key` | str | `None` | AWS secret key |
| `s3_endpoint_url` | str | `None` | Custom S3 endpoint (Wasabi, R2, etc.) |
