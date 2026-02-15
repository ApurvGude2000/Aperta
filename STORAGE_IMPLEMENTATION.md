# Storage Implementation - Complete Setup

## What Was Added

A complete **file persistence layer** that automatically saves:
1. **Audio files** to local filesystem or AWS S3
2. **Diarized transcripts** in text format
3. **Metadata** about recordings (duration, speaker count, timestamps)
4. **Database records** for conversations and speakers

---

## Files Created/Modified

### New Files
- `backend/services/storage.py` (350+ lines)
  - `StorageService` class for unified file storage
  - `StorageConfig` for backend configuration
  - Support for local filesystem and S3

- `STORAGE_GUIDE.md` (400+ lines)
  - Complete documentation
  - Setup instructions for local and S3
  - Cost estimates and optimization tips
  - Troubleshooting guide

### Modified Files
- `backend/api/routes/audio.py`
  - Added storage initialization
  - Updated `/audio/process` to save files
  - Added `/audio/storage-info` endpoint
  - Updated response to include file paths

- `backend/requirements.txt`
  - Added `aiofiles>=23.2.0` (async file I/O)
  - Added `boto3>=1.26.0` (S3 support, optional)

---

## Key Features

### 1. Unified Storage API
```python
storage = StorageService(config)

# Save audio
audio_path = await storage.save_audio_file(
    file_content=bytes,
    conversation_id="conv_123",
    filename="meeting.wav"
)

# Save transcript
transcript_path = await storage.save_transcript(
    transcript_text="Speaker 1: Hello...",
    conversation_id="conv_123"
)
```

### 2. Local Filesystem Storage (Development)
- **Default behavior** - no configuration needed
- **Location:** `./uploads/` directory
- **Structure:** Organized by conversation ID and date
- **Perfect for:** Development, testing, local demos

### 3. AWS S3 Storage (Production)
- **Enable via environment variables:**
  ```bash
  export AWS_ACCESS_KEY_ID="..."
  export AWS_SECRET_ACCESS_KEY="..."
  export S3_BUCKET_NAME="aperta-audio"
  ```
- **Automatic:** Detects S3 config and uses it
- **Fallback:** Gracefully falls back to local if S3 fails
- **Features:**
  - Server-side encryption
  - Automatic backups
  - Global access
  - Scalable to any size

### 4. S3-Compatible Services
- Works with **Wasabi**, **MinIO**, **Cloudflare R2**
- Set `S3_ENDPOINT_URL` for custom endpoints

### 5. Metadata Tracking
- **Audio metadata** (duration, speaker count, upload time)
- **Transcript metadata** (timestamps, conversation ID)
- **JSON metadata files** (local storage)
- **S3 object metadata** (S3 storage)

### 6. Database Integration
- Conversation records include `recording_url` (path to audio)
- Speaker/participant records created per speaker
- Supports transcript queries from database

---

## How It Works

### Upload Flow
```
1. User uploads audio file
   ↓
2. File validated & read into memory
   ↓
3. Audio processed (transcribe + diarize)
   ↓
4. Save to Storage (PARALLEL):
   ├─ Audio file → Local FS or S3
   ├─ Transcript → Local FS or S3
   └─ Metadata → JSON + Database
   ↓
5. Return response with file paths
   - audio_file_path: "./uploads/conv_123/.../meeting.wav"
   - transcript_file_path: "./uploads/conv_123/.../transcript.txt"
```

### Storage Selection
```
if S3_BUCKET and AWS_CREDENTIALS_SET:
    use S3 storage
else:
    use local filesystem storage

fallback:
    if S3 fails → try local filesystem
```

---

## API Response Format

### POST /audio/process

Now includes storage paths:

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

New endpoint for storage status:

```json
{
  "storage_type": "local",
  "local_path": "./uploads",
  "s3_bucket": null,
  "s3_enabled": false
}
```

---

## Configuration

### Development (Local Storage)
No configuration needed! Just run:
```bash
python main.py
```

Files automatically save to `./uploads/`

### Production (S3 Storage)

**Method 1: Environment variables**
```bash
export AWS_ACCESS_KEY_ID="your-key"
export AWS_SECRET_ACCESS_KEY="your-secret"
export S3_BUCKET_NAME="aperta-audio"
export S3_REGION="us-east-1"
```

**Method 2: .env file**
```env
AWS_ACCESS_KEY_ID=your-key
AWS_SECRET_ACCESS_KEY=your-secret
S3_BUCKET_NAME=aperta-audio
S3_REGION=us-east-1
```

**Method 3: Docker environment**
```dockerfile
ENV AWS_ACCESS_KEY_ID="..."
ENV AWS_SECRET_ACCESS_KEY="..."
```

---

## File Organization

### Local Filesystem
```
uploads/
├── conv_abc123/
│   ├── 2024/01/15/
│   │   ├── meeting.wav
│   │   ├── meeting_metadata.json
│   │   └── conv_abc123_transcript.txt
├── conv_xyz789/
│   ├── 2024/01/16/
│   │   └── presentation.mp3
```

### S3
```
s3://aperta-audio/
├── audio/
│   ├── conv_abc123/2024/01/15/meeting.wav
│   └── conv_xyz789/2024/01/16/presentation.mp3
└── transcripts/
    ├── conv_abc123/2024/01/15/conv_abc123_transcript.txt
    └── conv_xyz789/2024/01/16/conv_xyz789_transcript.txt
```

---

## Database Integration

### Conversation Model Update
- `recording_url` now contains path to saved audio file
- Example: `./uploads/conv_123/2024/01/15/meeting.wav`

### Query Example
```python
# Get all conversations with their audio files
conversations = await db.execute(
    select(Conversation).filter(Conversation.status == "completed")
)
for conv in conversations.scalars().all():
    print(f"Transcript: {conv.transcript}")
    print(f"Audio at: {conv.recording_url}")
```

---

## Cost Breakdown

### Local Storage
- **Cost:** FREE ✅
- **Best for:** Development, testing
- **Limitation:** Single machine only

### S3 Storage
- **Storage:** $0.023/GB/month
- **Requests:** ~$0.005 per 1,000 PUTs, $0.0004 per 1,000 GETs
- **Example:** 10 hours audio/month (~6GB)
  - Estimated: ~$0.29/month
- **Best for:** Production, scalability, global access

### S3-Compatible (Wasabi)
- **Cost:** $0.0047/GB/month (cheaper)
- **No request fees**
- **Example:** Same 10 hours = ~$0.03/month
- **Bonus:** Faster uploads with global edge cache

---

## Usage Examples

### Upload Audio (saves automatically)
```bash
curl -X POST http://localhost:8000/audio/process \
  -F "file=@meeting.wav"
```

Response includes:
```json
{
  "audio_file_path": "./uploads/conv_xyz/...",
  "transcript_file_path": "./uploads/conv_xyz/..."
}
```

### Check Storage Status
```bash
curl http://localhost:8000/audio/storage-info
```

### Retrieve Audio File (from local storage)
```bash
cat uploads/conv_xyz/2024/01/15/meeting.wav
```

### Retrieve Transcript
```bash
cat uploads/conv_xyz/2024/01/15/conv_xyz_transcript.txt
```

---

## Async/Concurrent Operations

The storage service uses `aiofiles` for **non-blocking I/O**, meaning:
- Multiple uploads can be processed simultaneously
- Saving to storage doesn't block transcription
- Database operations happen in parallel
- Maximum throughput for high-traffic scenarios

---

## Error Handling

### Graceful Fallbacks
```
S3 upload fails?
  → Automatically fall back to local filesystem
  → Log warning and continue
  → User still gets successful response
```

### Missing Directory
```
Directory doesn't exist?
  → Automatically created (with parents)
  → No manual setup required
```

### S3 Connection Issues
```
AWS credentials invalid?
  → S3 automatically disabled
  → Fall back to local storage
  → Log details for debugging
```

---

## Security Features

### Local Storage
- File permissions via OS
- Access restricted by user/group
- No internet exposure

### S3 Storage
- Server-side encryption (AES-256)
- Bucket-level access control
- IAM policies for fine-grained permissions
- Versioning support for recovery
- Access logging available

### Best Practices
1. Use IAM roles instead of access keys
2. Enable versioning on S3 bucket
3. Set bucket lifecycle policies
4. Rotate credentials quarterly
5. Monitor S3 access logs

---

## Monitoring

### Check Storage Info
```bash
curl http://localhost:8000/audio/storage-info
```

### Monitor Local Storage
```bash
# Show all files
find uploads -type f

# Show total size
du -sh uploads/

# Show files by conversation
du -sh uploads/conv_*/
```

### Monitor S3
```bash
# List all audio files
aws s3 ls s3://aperta-audio/audio/ --recursive

# Get bucket size
aws s3api list-objects-v2 \
  --bucket aperta-audio \
  --summarize
```

---

## Testing

### Test Local Storage (Default)
```bash
# Just run - should work automatically
python main.py

# Upload audio
curl -X POST http://localhost:8000/audio/process \
  -F "file=@test_audio.wav"

# Check files saved
ls -la uploads/
```

### Test S3 Storage
```bash
# Set credentials
export AWS_ACCESS_KEY_ID="..."
export AWS_SECRET_ACCESS_KEY="..."
export S3_BUCKET_NAME="test-bucket"

# Run
python main.py

# Upload
curl -X POST http://localhost:8000/audio/process \
  -F "file=@test_audio.wav"

# Verify in S3
aws s3 ls s3://test-bucket/ --recursive
```

---

## Future Enhancements

### Short-term (P2)
- [ ] Cleanup old files (retention policies)
- [ ] Compress transcripts to save space
- [ ] Add file encryption at rest
- [ ] Implement versioning

### Medium-term (P3)
- [ ] Archive to Glacier after 90 days
- [ ] CDN distribution for fast access
- [ ] Virus scanning for uploads
- [ ] Bandwidth caching with CloudFront

### Long-term (P4)
- [ ] Multi-region replication
- [ ] Disaster recovery setup
- [ ] Cost optimization with analysis
- [ ] Data governance dashboard

---

## Troubleshooting

### Files not saving?
1. Check logs: `grep -i storage backend.log`
2. Verify directory exists: `ls -la uploads/`
3. Check permissions: `chmod -R 755 uploads/`

### S3 not working?
1. Verify credentials: `aws s3 ls`
2. Check bucket exists: `aws s3 ls`
3. Verify bucket policy allows PutObject

### Out of disk space?
1. Check size: `du -sh uploads/`
2. Archive old files to S3
3. Delete files older than X days
4. Move to external storage

---

## Summary

✅ **What You Get:**
- Automatic audio file persistence
- Automatic transcript persistence
- Choice of local or S3 storage
- Database integration
- Production-ready error handling
- Complete documentation

✅ **What's Included:**
- `StorageService` with full async I/O
- Support for local and S3 backends
- Automatic metadata tracking
- Database integration
- Graceful error handling and fallbacks

✅ **Next Steps:**
1. Upload audio via `/audio/process`
2. Check response for file paths
3. Retrieve files from storage
4. Configure S3 for production
5. Monitor storage usage

---

## Related Documentation
- `STORAGE_GUIDE.md` - Detailed setup and usage guide
- `AUDIO_PROCESSING.md` - Audio processing pipeline
- `AUDIO_ARCHITECTURE.md` - System architecture

