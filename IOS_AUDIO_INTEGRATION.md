# iOS Audio Integration Guide

Complete guide for integrating audio recording and upload into the Aperta iOS app.

## Overview

The iOS audio system consists of:
1. **Event Recording** - Using AVAudioEngine/AVAudioRecorder
2. **File Management** - EventStorageManager for local storage
3. **Upload Service** - AudioUploadService for backend communication
4. **Upload UI** - AudioUploadView for user interaction

## Architecture

```
PastEventsView
    ↓
EventDetail (View Past Event)
    ↓
AudioUploadView (Upload Recording)
    ↓
AudioUploadService (HTTP Upload)
    ↓
Backend API (/audio/process-event)
    ↓
Database + S3 Storage
```

## Integration Steps

### Step 1: Add AudioUploadService to Your Project

The `AudioUploadService.swift` file is already included in the project.

**Location:** `ApertaMobile/Aperta/AudioUploadService.swift`

This service handles:
- Multipart form data encoding
- File upload to backend
- Progress tracking
- Error handling
- Response parsing

### Step 2: Add AudioUploadView to Event Detail

Add the audio upload UI to your event detail or past events view.

**Example: Adding to PastEventsView**

```swift
import SwiftUI

struct PastEventsView: View {
    @State private var selectedEvent: Event?
    @State private var showAudioUpload = false

    var body: some View {
        NavigationStack {
            VStack {
                // Event list
                List(events) { event in
                    HStack {
                        VStack(alignment: .leading) {
                            Text(event.name)
                                .font(.headline)
                            Text(event.location)
                                .font(.caption)
                                .foregroundColor(.gray)
                        }
                        Spacer()
                        Button(action: {
                            selectedEvent = event
                            showAudioUpload = true
                        }) {
                            Image(systemName: "arrow.up.circle")
                                .foregroundColor(.blue)
                        }
                    }
                }
            }
            .sheet(isPresented: $showAudioUpload) {
                if let event = selectedEvent {
                    AudioUploadView(event: event)
                }
            }
        }
    }
}
```

### Step 3: Configure Backend URL

Edit `AudioUploadService.swift` to point to your backend:

```swift
class AudioUploadService: NSObject, ObservableObject {
    // Change this to your actual backend URL
    private let baseURL = "http://localhost:8000"

    // Or use environment-based configuration:
    private var baseURL: String {
        #if DEBUG
        return "http://localhost:8000"  // Local development
        #else
        return "https://api.aperta.app"  // Production
        #endif
    }
}
```

### Step 4: Test the Upload

1. **Start backend:**
   ```bash
   cd backend
   python main.py
   ```

2. **Run iOS app:**
   ```bash
   # In Xcode: Product > Run (or Cmd+R)
   ```

3. **Upload audio:**
   - Create or view an event
   - Tap "Upload Audio" button
   - Select audio file
   - Tap "Upload Audio"
   - Check for success message

## Using Existing Recordings

If you have recording files from the EventCreationView:

```swift
// From EventStorageManager
let recordingsFolder = EventStorageManager.shared.recordingsFolder(for: event)

// Get audio files from folder
if let audioFiles = try? FileManager.default.contentsOfDirectory(
    at: recordingsFolder,
    includingPropertiesForKeys: nil
) {
    for audioFile in audioFiles {
        if audioFile.pathExtension == "m4a" {
            // Upload this file
            Task {
                let result = await AudioUploadService.shared.uploadAudioFile(
                    audioFile,
                    eventName: event.name,
                    location: event.location
                )
                // Handle result
            }
        }
    }
}
```

## Advanced: Batch Upload Multiple Recordings

```swift
func uploadAllEventRecordings(_ event: Event) async {
    let service = AudioUploadService.shared
    let folder = EventStorageManager.shared.recordingsFolder(for: event)

    guard let files = try? FileManager.default.contentsOfDirectory(
        at: folder,
        includingPropertiesForKeys: nil
    ) else {
        print("No recordings found")
        return
    }

    for file in files where file.pathExtension == "m4a" {
        print("Uploading \(file.lastPathComponent)...")

        let result = await service.uploadAudioFile(
            file,
            eventName: event.name,
            location: event.location
        )

        switch result {
        case .success(let response):
            print("✅ Uploaded: \(response.conversation_id)")
            // Store conversation ID for later reference
            event.conversationIds.append(response.conversation_id)

        case .failure(let error):
            print("❌ Upload failed: \(error.localizedDescription)")
            // Continue with next file
            continue
        }
    }
}
```

## Response Handling

After successful upload, the backend returns:

```json
{
  "conversation_id": "conv_xxx",
  "audio_recording": {
    "id": "rec_xxx",
    "file_path": "s3://bucket/audio/...",
    "duration": 1234.5,
    "processing_status": "completed"
  },
  "transcription": {
    "id": "trans_xxx",
    "formatted_text": "Speaker A: ...",
    "speaker_count": 2,
    "speaker_names": {"1": "Speaker A", "2": "Speaker B"},
    "sentiment": "positive",
    "summary": "Meeting discussed...",
    "entities": [...],
    "action_items": [...]
  },
  "ai_analysis": {
    "summary": "...",
    "sentiment": "positive",
    "confidence_score": 0.89
  }
}
```

**Use this data in your app:**

```swift
struct ConversationRecord: Codable {
    let conversation_id: String
    let audio_recording: AudioRecordingData
    let transcription: TranscriptionData
    let ai_analysis: AIAnalysisData
}

// Store in your Event model
struct Event: Codable {
    let id: UUID
    var name: String
    var location: String
    var date: Date
    var recordings: [Recording]

    // Add this field
    var uploadedConversations: [ConversationRecord] = []
}
```

## Handling Upload Errors

The `AudioUploadService` provides detailed error information:

```swift
enum AudioUploadError: LocalizedError {
    case fileNotFound
    case invalidResponse
    case serverError(String)
    case processingError(String)
    case networkError
}
```

**Handle errors in your view:**

```swift
if let error = uploadService.uploadError {
    VStack {
        Image(systemName: "exclamationmark.circle.fill")
            .foregroundColor(.red)
        Text(error)
            .font(.caption)
    }
    .padding()
    .background(Color.red.opacity(0.1))
    .cornerRadius(8)

    // Retry button
    Button("Retry Upload") {
        uploadService.uploadError = nil
        uploadAudio()
    }
}
```

## Progress Tracking

Monitor upload progress:

```swift
@Published var uploadProgress: Double = 0.0  // 0.0 to 1.0

// In your view
if uploadService.isUploading {
    ProgressView(value: uploadService.uploadProgress)
    Text("\(Int(uploadService.uploadProgress * 100))%")
}
```

## Network Handling

The service automatically handles:
- ✅ Network failures with retry logic
- ✅ Timeout handling (5 min default)
- ✅ Background task support
- ✅ WiFi preference option (configurable)

**Enable WiFi-only uploads:**

```swift
var shouldWaitForWiFi: Bool {
    #if DEBUG
    return false  // Allow cellular in debug
    #else
    return true   // WiFi only in production
    #endif
}
```

## Security Considerations

### HTTPS in Production

Ensure backend uses HTTPS in production:

```swift
private var baseURL: String {
    #if DEBUG
    return "http://localhost:8000"
    #else
    return "https://api.aperta.app"  // Always use HTTPS
    #endif
}
```

### Certificate Pinning (Optional)

For enhanced security, implement certificate pinning:

```swift
import CryptoKit

// Add public key pinning for production
func setupCertificatePinning() {
    let delegate = CertificatePinningDelegate(
        expectedPublicKeyHashes: ["sha256/xxxx..."]
    )
    urlSession = URLSession(configuration: config, delegate: delegate)
}
```

### Data Encryption

Audio files are encrypted:
1. In transit: TLS/HTTPS
2. At rest: S3 server-side encryption
3. User consent: Must acknowledge recording

## Testing

### Unit Tests

```swift
import XCTest

class AudioUploadServiceTests: XCTestCase {
    let service = AudioUploadService.shared

    func testUploadFile() async throws {
        let testFile = URL(fileURLWithPath: "/path/to/test.wav")

        let result = await service.uploadAudioFile(testFile)

        switch result {
        case .success(let response):
            XCTAssertNotNil(response.conversation_id)
            XCTAssertEqual(response.audio_recording.processing_status, "completed")
        case .failure(let error):
            XCTFail("Upload failed: \(error)")
        }
    }

    func testInvalidFile() async throws {
        let invalidFile = URL(fileURLWithPath: "/nonexistent/file.wav")

        let result = await service.uploadAudioFile(invalidFile)

        switch result {
        case .failure(.fileNotFound):
            // Expected
            break
        default:
            XCTFail("Should return fileNotFound error")
        }
    }
}
```

### Integration Tests

```swift
func testEndToEndAudioUpload() async throws {
    // 1. Create test event
    let event = Event(
        name: "Test Event",
        location: "Test Location",
        date: Date()
    )

    // 2. Save event
    try EventStorageManager.shared.saveEvent(event)

    // 3. Create test audio file
    let testAudioURL = createTestAudioFile()

    // 4. Upload
    let service = AudioUploadService.shared
    let result = await service.uploadAudioFile(
        testAudioURL,
        eventName: event.name,
        location: event.location
    )

    // 5. Verify
    switch result {
    case .success(let response):
        XCTAssertFalse(response.conversation_id.isEmpty)
        XCTAssertEqual(response.transcription.speaker_count, 0) // Or actual count
    case .failure(let error):
        XCTFail("Upload failed: \(error)")
    }
}
```

## Performance Tips

1. **Compress audio before upload:**
   ```swift
   // Use lower bitrate (64-128 kbps) for faster upload
   let settings = [
       AVFormatIDKey: kAudioFormatMPEG4AAC,
       AVEncoderBitRateKey: 64000,  // 64 kbps
       AVSampleRateKey: 16000,       // 16 kHz
       AVNumberOfChannelsKey: 1      // Mono
   ]
   ```

2. **Upload only on WiFi in production:**
   ```swift
   // Check network type before uploading
   var isOnWiFi: Bool {
       // Check using NetworkFramework or Reachability
   }
   ```

3. **Show upload progress:**
   ```swift
   // Users appreciate knowing upload is in progress
   if uploadService.isUploading {
       ProgressView(value: uploadService.uploadProgress)
           .animation(.linear, value: uploadService.uploadProgress)
   }
   ```

## Troubleshooting

### Upload Takes Too Long

**Cause:** Large file size or slow network

**Solution:**
- Compress audio (lower bitrate)
- Upload only on WiFi
- Increase timeout in `AudioUploadService`

### Connection Refused

**Cause:** Backend not running or wrong URL

**Solution:**
```bash
# Check backend is running
curl http://localhost:8000/health

# Update URL in AudioUploadService
private let baseURL = "http://<your-ip>:8000"
```

### File Not Found Error

**Cause:** Audio file path is incorrect

**Solution:**
```swift
// Verify file exists
let fileExists = FileManager.default.fileExists(atPath: audioURL.path)
print("File exists: \(fileExists)")
print("File path: \(audioURL.path)")
```

### Multipart Form Data Error

**Cause:** Incorrect boundary or content type

**Solution:** Check `AudioUploadService._buildMultipartRequest()` implementation

## Future Enhancements

- [ ] Add recording playback with thumbnail waveform
- [ ] Add local audio editing (trim, cut, enhance)
- [ ] Add automatic background upload
- [ ] Add upload queue for multiple files
- [ ] Add speaker name auto-suggestion from contacts
- [ ] Add audio metadata (duration, size, format) display
- [ ] Add cancel/pause upload functionality
- [ ] Add bandwidth throttling for cellular

## Related Files

- Backend: `backend/api/routes/audio.py`
- Frontend: `frontend/src/components/AudioTranscriptionViewer.tsx`
- Documentation: `AUDIO_SYSTEM.md`
- Setup Guide: `AUDIO_SETUP.md`
