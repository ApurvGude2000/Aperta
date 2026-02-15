# Audio Processing Setup Guide

Complete setup instructions for the audio processing and speaker diarization pipeline.

## Overview

The audio pipeline requires several large ML models:
1. **Whisper** (OpenAI) - Speech-to-text transcription
2. **Pyannote** - Speaker diarization (identifying who is speaking)
3. **Librosa** - Audio loading and preprocessing

## Prerequisites

- Python 3.9+
- pip or conda
- ~4GB disk space for models
- 8GB+ RAM (16GB+ recommended)
- GPU support optional but recommended (CUDA 11.8+ for faster processing)

## Step 1: Install Python Dependencies

```bash
cd backend
pip install -r requirements.txt
```

This installs:
- `openai-whisper` - Speech transcription
- `pyannote.audio` - Speaker diarization
- `librosa` - Audio loading
- `torch` - Deep learning framework
- `numpy` - Numerical computing

## Step 2: Accept Pyannote License

Pyannote requires explicit license acceptance from HuggingFace.

### Step 2a: Create HuggingFace Account

1. Visit https://huggingface.co/join
2. Sign up with email or GitHub/Google account

### Step 2b: Accept Pyannote License

1. Visit https://huggingface.co/pyannote/speaker-diarization-3.0
2. Click "Accept repository"
3. Agree to the license terms

### Step 2c: Get Your HF Token

1. Visit https://huggingface.co/settings/tokens
2. Click "New token"
3. Set name: "aperta" or "aperta-audio"
4. Set role: "read" (only needs to download models)
5. Click "Create token"
6. Copy the token (looks like `hf_xxxxxxxxxxxxxxxxxxxxx`)

### Step 2d: Set Environment Variable

```bash
# macOS/Linux
export HF_TOKEN="hf_xxxxxxxxxxxxxxxxxxxxx"

# Windows (PowerShell)
$env:HF_TOKEN = "hf_xxxxxxxxxxxxxxxxxxxxx"

# Add to ~/.bashrc or ~/.zshrc for persistence
echo 'export HF_TOKEN="hf_xxxxxxxxxxxxxxxxxxxxx"' >> ~/.bashrc
```

## Step 3: Optional - GPU Setup (Recommended)

### macOS (Apple Silicon)

GPU support is automatic on M1/M2/M3 Macs.

```bash
# No additional setup needed
# Torch will use Metal acceleration automatically
```

### macOS/Linux (NVIDIA GPU)

Requires CUDA toolkit.

```bash
# Install CUDA 11.8+ following:
# https://developer.nvidia.com/cuda-11-8-0-download-wizard

# Verify installation
nvidia-smi
```

### Windows (NVIDIA GPU)

```bash
# Install CUDA from:
# https://developer.nvidia.com/cuda-11-8-0-download-wizard

# Verify installation
nvidia-smi
```

## Step 4: Test Installation

### Test 1: Import Modules

```bash
python -c "
import torch
print(f'PyTorch: {torch.__version__}')
print(f'CUDA available: {torch.cuda.is_available()}')

import whisper
print('Whisper: OK')

import pyannote.audio
print('Pyannote: OK')

import librosa
print('Librosa: OK')
"
```

Expected output:
```
PyTorch: 2.x.x
CUDA available: True/False
Whisper: OK
Pyannote: OK
Librosa: OK
```

### Test 2: Download Models

First run will download models (~3GB total). This takes a few minutes.

```bash
python -c "
import whisper
print('Downloading Whisper model...')
whisper.load_model('small')
print('Whisper downloaded successfully')
"
```

### Test 3: Test with Sample Audio

Create a simple test audio file or use an existing one:

```bash
python backend/examples/audio_processing_example.py /path/to/test_audio.wav
```

This will:
1. Load the audio file
2. Transcribe it with Whisper
3. Identify speakers with Pyannote
4. Print formatted results

## Step 5: Start Backend Server

```bash
cd backend
python main.py
```

Expected output:
```
INFO: Uvicorn running on http://0.0.0.0:8000
INFO: Audio processor initialized successfully
```

## Step 6: Test API Endpoint

### Using curl

```bash
curl -X POST http://localhost:8000/audio/process \
  -F "file=@/path/to/audio.wav"
```

### Using Python

```python
import requests

with open("path/to/audio.wav", "rb") as f:
    response = requests.post(
        "http://localhost:8000/audio/process",
        files={"file": f}
    )

print(response.json())
```

### Expected Response

```json
{
    "conversation_id": "conv_abc123...",
    "message": "Successfully processed audio with 2 speakers",
    "transcript": {
        "conversation_id": "conv_abc123...",
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
        "speaker_count": 2,
        "speaker_names": {"1": "Speaker 1", "2": "Speaker 2"},
        "total_duration": 120.5,
        "formatted_transcript": "Speaker 1: [00:00-00:05] Hello everyone...",
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

## Troubleshooting

### Issue: "HuggingFace token not found"

**Symptom:**
```
RuntimeError: You need to provide your Hugging Face token to access this model.
```

**Solution:**
1. Check token is set: `echo $HF_TOKEN`
2. Ensure it starts with `hf_`
3. Create new token at https://huggingface.co/settings/tokens
4. Set environment variable again: `export HF_TOKEN="hf_..."`

### Issue: "CUDA out of memory"

**Symptom:**
```
RuntimeError: CUDA out of memory
```

**Solution:**
1. Restart the server to free GPU memory
2. Use CPU instead: Set `CUDA_VISIBLE_DEVICES=""` before running
3. Process shorter audio files
4. Consider using quantized models (not yet implemented)

### Issue: "ModuleNotFoundError: No module named 'whisper'"

**Symptom:**
```
ModuleNotFoundError: No module named 'openai.whisper'
```

**Solution:**
1. Ensure requirements installed: `pip install -r requirements.txt`
2. Check Python version: `python --version` (need 3.9+)
3. Try reinstalling: `pip install openai-whisper --upgrade --force-reinstall`

### Issue: "Pyannote license not accepted"

**Symptom:**
```
OSError: You need to accept the model license to access this model
```

**Solution:**
1. Visit https://huggingface.co/pyannote/speaker-diarization-3.0
2. Click "Accept repository"
3. Login with same HF account you created token for
4. Create new token at https://huggingface.co/settings/tokens

### Issue: Audio processing is very slow

**Symptom:**
```
[0/100] Transcribing... (takes minutes)
```

**Reason:** Using CPU instead of GPU

**Solution:**
1. Check CUDA setup: `nvidia-smi` or `python -c "import torch; print(torch.cuda.is_available())"`
2. Install CUDA if GPU available
3. For Apple Silicon: Torch uses Metal acceleration automatically
4. Processing ~1 minute per minute of audio is normal on CPU

### Issue: "librosa.audiobasics.AudioLoadingException"

**Symptom:**
```
librosa.audiobasics.AudioLoadingException: could not load file
```

**Reason:** Unsupported audio format

**Solution:**
1. Supported formats: WAV, MP3, FLAC, OGG, M4A, AAC, WMA
2. Convert audio: `ffmpeg -i input.wav -acodec pcm_s16le -ar 16000 output.wav`
3. Ensure file is not corrupted

## Performance Benchmarks

Typical processing times (for 10-minute conversation):

### GPU (NVIDIA RTX 3080)
- Transcription: ~2 seconds
- Diarization: ~5 seconds
- Total: ~10 seconds

### GPU (Apple Silicon M1)
- Transcription: ~5 seconds
- Diarization: ~8 seconds
- Total: ~15 seconds

### CPU (Intel i7)
- Transcription: ~30 seconds
- Diarization: ~45 seconds
- Total: ~90 seconds

## Next Steps

1. **Test the API**: Upload sample audio and verify transcription
2. **Identify speakers**: Use `/audio/identify-speakers/` to add names
3. **Analyze conversations**: Use `/conversations/{id}/analyze` to run all agents
4. **Integrate with frontend**: Frontend uploads audio to `/audio/process`

## Additional Resources

- [Whisper Documentation](https://github.com/openai/whisper)
- [Pyannote Documentation](https://github.com/pyannote/pyannote-audio)
- [Librosa Documentation](https://librosa.org/)
- [HuggingFace Account Setup](https://huggingface.co/join)
