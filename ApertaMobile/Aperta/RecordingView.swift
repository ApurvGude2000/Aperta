import SwiftUI

struct RecordingView: View {
    let event: Event
    let onEndEvent: () -> Void
    @StateObject private var recorder = SimpleWhisperRecorder()
    @StateObject private var uploadService = AudioUploadService.shared
    @State private var showError = false
    @State private var hasRecordedOnce = false
    @State private var currentEvent: Event
    @State private var recordingToDelete: Recording?
    @State private var recordingToRename: Recording?
    @State private var newRecordingName = ""
    @State private var showDeleteConfirmation = false
    @State private var showRenameDialog = false
    @State private var uploadStatus = ""
    @Environment(\.dismiss) private var dismiss

    init(event: Event, onEndEvent: @escaping () -> Void) {
        self.event = event
        self.onEndEvent = onEndEvent
        _currentEvent = State(initialValue: event)
    }
    
    var body: some View {
        VStack(spacing: 20) {
            // Event info header
            VStack(spacing: 8) {
                HStack {
                    Image(systemName: "calendar.circle.fill")
                        .foregroundColor(.blue)
                    Text("Recording Session")
                        .font(.caption)
                        .foregroundColor(.gray)
                        .textCase(.uppercase)
                }

                Text(event.name)
                    .font(.title2)
                    .bold()
                    .multilineTextAlignment(.center)

                HStack(spacing: 16) {
                    HStack(spacing: 4) {
                        Image(systemName: "location.fill")
                            .font(.caption)
                        Text(event.location)
                            .font(.subheadline)
                    }

                    if !currentEvent.recordings.isEmpty {
                        HStack(spacing: 4) {
                            Image(systemName: "waveform.circle.fill")
                                .font(.caption)
                            Text("\(currentEvent.recordings.count) recording\(currentEvent.recordings.count == 1 ? "" : "s")")
                                .font(.subheadline)
                        }
                    }
                }
                .foregroundColor(.gray)
            }
            .padding()
            .frame(maxWidth: .infinity)
            .background(Color.blue.opacity(0.05))
            .cornerRadius(12)
            .padding(.horizontal)
            .padding(.top)

            // Recordings list (if any exist)
            if !currentEvent.recordings.isEmpty {
                VStack(alignment: .leading, spacing: 8) {
                    Text("Recordings")
                        .font(.headline)
                        .padding(.horizontal)

                    ScrollView {
                        VStack(spacing: 8) {
                            ForEach(Array(currentEvent.recordings.enumerated()), id: \.element.id) { index, recording in
                                HStack(spacing: 12) {
                                    // Recording info
                                    VStack(alignment: .leading, spacing: 4) {
                                        Text(recording.name.isEmpty ? "Recording \(index + 1)" : recording.name)
                                            .font(.subheadline)
                                            .fontWeight(.medium)

                                        HStack(spacing: 8) {
                                            if let duration = recording.duration {
                                                Text(formatDuration(duration))
                                                    .font(.caption)
                                                    .foregroundColor(.gray)
                                            }

                                            Text("\(recording.transcript.count) chars")
                                                .font(.caption)
                                                .foregroundColor(.gray)
                                        }
                                    }

                                    Spacer()

                                    // Action buttons
                                    HStack(spacing: 8) {
                                        Button(action: {
                                            recordingToRename = recording
                                            newRecordingName = recording.name.isEmpty ? "Recording \(index + 1)" : recording.name
                                            showRenameDialog = true
                                        }) {
                                            Image(systemName: "pencil")
                                                .font(.caption)
                                                .foregroundColor(.blue)
                                                .padding(8)
                                                .background(Color.blue.opacity(0.1))
                                                .cornerRadius(6)
                                        }

                                        Button(action: {
                                            recordingToDelete = recording
                                            showDeleteConfirmation = true
                                        }) {
                                            Image(systemName: "trash")
                                                .font(.caption)
                                                .foregroundColor(.red)
                                                .padding(8)
                                                .background(Color.red.opacity(0.1))
                                                .cornerRadius(6)
                                        }
                                    }
                                }
                                .padding()
                                .background(Color.gray.opacity(0.05))
                                .cornerRadius(8)
                            }
                        }
                        .padding(.horizontal)
                    }
                    .frame(maxHeight: 200)
                }
                .padding(.vertical, 8)
            }

            // Fixed-height container for transcript and visual feedback
            ZStack(alignment: .center) {
                // Background: Transcript display (always visible)
                ScrollView {
                    if recorder.transcriptionText.isEmpty {
                        VStack(spacing: 16) {
                            Spacer()
                                .frame(height: recorder.isRecording ? 130 : 20)

                            Image(systemName: recorder.isRecording ? "waveform.circle" : "mic.circle")
                                .font(.system(size: 60))
                                .foregroundColor(.gray.opacity(0.5))

                            VStack(spacing: 8) {
                                Text(recorder.isRecording ? "Listening..." : "Ready to Record")
                                    .font(.headline)
                                    .foregroundColor(.gray)

                                Text(recorder.isRecording ? "Speak naturally. Transcription will appear here after you stop." : "Tap 'Start Recording' to begin capturing your conversation")
                                    .font(.caption)
                                    .foregroundColor(.gray)
                                    .multilineTextAlignment(.center)
                                    .padding(.horizontal)
                            }
                            Spacer()
                        }
                        .frame(maxWidth: .infinity, minHeight: 300)
                    } else {
                        VStack {
                            if recorder.isRecording {
                                Spacer().frame(height: 130)
                            }
                            Text(recorder.transcriptionText)
                                .frame(maxWidth: .infinity, alignment: .leading)
                        }
                        .padding()
                    }
                }
                .frame(height: 300)
                .background(Color.gray.opacity(0.1))
                .cornerRadius(10)

                // Foreground: Visual feedback (overlaid when recording)
                if recorder.isRecording {
                    VStack(spacing: 8) {
                        // Timer and indicator
                        HStack(spacing: 12) {
                            PulsingRecordIndicator(isRecording: recorder.isRecording)
                            RecordingTimerView(duration: recorder.recordingDuration)
                        }
                        .padding(.top, 8)

                        // Waveform visualization
                        WaveformView(level: recorder.audioLevel)
                            .frame(height: 60)
                            .padding(.horizontal, 8)

                        // Audio level meter
                        HStack {
                            Image(systemName: "speaker.wave.2.fill")
                                .font(.caption)
                                .foregroundColor(.gray)
                            AudioLevelMeter(level: recorder.audioLevel)
                        }
                        .padding(.bottom, 8)

                        Spacer()
                    }
                    .frame(maxWidth: .infinity)
                    .background(
                        LinearGradient(
                            colors: [Color.gray.opacity(0.15), Color.clear],
                            startPoint: .top,
                            endPoint: .bottom
                        )
                    )
                    .cornerRadius(10)
                }

                // Model loading overlay (doesn't affect layout)
                if !recorder.isModelLoaded {
                    VStack(spacing: 12) {
                        ProgressView(value: recorder.modelLoadingProgress)
                            .progressViewStyle(.linear)
                            .frame(width: 200)
                        Text("Loading Whisper Model...")
                            .font(.subheadline)
                            .foregroundColor(.gray)
                    }
                    .padding()
                    .background(Color(.systemBackground).opacity(0.95))
                    .cornerRadius(12)
                    .shadow(radius: 10)
                }
            }

            Spacer()
                .frame(minHeight: 20)

            // Recording controls - FIXED POSITION (no jumping!)
            VStack(spacing: 12) {
                // Main recording button(s) - FIXED HEIGHT CONTAINER
                ZStack {
                    if !recorder.isRecording {
                        // Start recording button
                        Button(action: {
                            Task {
                                do {
                                    try await recorder.startRecording()
                                } catch {
                                    showError = true
                                }
                            }
                        }) {
                            HStack {
                                Image(systemName: "mic.circle.fill")
                                    .font(.title)
                                Text(hasRecordedOnce ? "Start New Recording" : "Start Recording")
                            }
                            .frame(maxWidth: .infinity)
                            .frame(height: 56)
                            .background(Color.blue)
                            .foregroundColor(.white)
                            .cornerRadius(10)
                        }
                        .disabled(!recorder.isModelLoaded || recorder.isTranscribing)
                    } else {
                        // Pause/Continue and Stop buttons (when recording)
                        HStack(spacing: 12) {
                            // Pause/Continue button
                            Button(action: {
                                if recorder.isPaused {
                                    try? recorder.resumeRecording()
                                } else {
                                    recorder.pauseRecording()
                                }
                            }) {
                                HStack {
                                    Image(systemName: recorder.isPaused ? "play.circle.fill" : "pause.circle.fill")
                                        .font(.title2)
                                    Text(recorder.isPaused ? "Continue" : "Pause")
                                }
                                .frame(maxWidth: .infinity)
                                .frame(height: 56)
                                .background(Color.orange)
                                .foregroundColor(.white)
                                .cornerRadius(10)
                            }

                            // Stop & Save button
                            Button(action: {
                                Task {
                                    do {
                                        // Get recording data
                                        let recordingData = try await recorder.stopRecordingAndGetData()

                                        // Generate default recording name
                                        let recordingNumber = currentEvent.recordings.count + 1
                                        let defaultName = "Recording \(recordingNumber)"

                                        // Create Recording object
                                        var newRecording = Recording(
                                            name: defaultName,
                                            transcript: recordingData.transcript,
                                            segments: recordingData.segments,
                                            audioFilePath: recordingData.audioFilePath,
                                            startTime: recordingData.startTime
                                        )

                                        // Set end time
                                        newRecording.endTime = recordingData.endTime

                                        // Add to CURRENT event (not the original)
                                        var updatedEvent = currentEvent
                                        updatedEvent.recordings.append(newRecording)

                                        // Save updated event
                                        try EventStorageManager.shared.saveEvent(updatedEvent)

                                        // Update current event state
                                        currentEvent = updatedEvent

                                        hasRecordedOnce = true

                                        print("✅ Recording saved: \(newRecording.id)")
                                        print("📝 Transcript (\(recordingData.transcript.count) chars): \(recordingData.transcript.prefix(100))...")
                                        print("🎵 Audio saved at: \(recordingData.audioFilePath)")
                                        print("📊 Event now has \(currentEvent.recordings.count) recording(s)")

                                        // CRITICAL: Run PII redaction BEFORE upload
                                        uploadStatus = "Redacting PII..."
                                        print("🔒 Running PII Guardian on transcript...")
                                        let redactedTranscript = await LLMModelManager.shared.redactPII(from: recordingData.transcript)
                                        print("🔒 PII redaction complete (\(redactedTranscript.count) chars)")

                                        // Auto-upload redacted transcript (NO audio file for privacy)
                                        uploadStatus = "Uploading to cloud..."
                                        let result = await uploadService.uploadTranscriptOnly(
                                            transcriptText: redactedTranscript,
                                            eventName: event.name,
                                            location: event.location
                                        )

                                        switch result {
                                        case .success(let response):
                                            uploadStatus = "✓ Uploaded (PII-protected)"
                                            print("✅ Upload successful: \(response.message)")
                                            print("📄 Saved to: \(response.transcript_file_path)")
                                        case .failure(let error):
                                            uploadStatus = "✗ Upload failed: \(error.localizedDescription)"
                                            print("❌ Upload failed: \(error)")
                                        }

                                    } catch {
                                        showError = true
                                        print("❌ Error saving recording: \(error)")
                                    }
                                }
                            }) {
                                HStack {
                                    Image(systemName: "stop.circle.fill")
                                        .font(.title2)
                                    Text("Stop & Save")
                                }
                                .frame(maxWidth: .infinity)
                                .frame(height: 56)
                                .background(Color.red)
                                .foregroundColor(.white)
                                .cornerRadius(10)
                            }
                        }
                    }
                }
                .frame(height: 56)

                // End event button
                Button(action: {
                    onEndEvent()
                    dismiss()
                }) {
                    Text("End Event")
                        .frame(maxWidth: .infinity)
                        .padding()
                        .background(Color.gray.opacity(0.2))
                        .foregroundColor(.primary)
                        .cornerRadius(10)
                }
            }
            .padding(.horizontal)
            .padding(.top, 20)

            // Status indicators
            VStack(spacing: 8) {
                if recorder.isTranscribing {
                    HStack {
                        ProgressView()
                        Text("Transcribing...")
                    }
                }

                if uploadService.isUploading {
                    HStack {
                        ProgressView()
                        Text("Uploading to cloud...")
                    }
                }

                if !uploadStatus.isEmpty && !uploadService.isUploading {
                    Text(uploadStatus)
                        .font(.caption)
                        .foregroundColor(uploadStatus.starts(with: "✓") ? .green : .red)
                }
            }
        }
        .padding()
        .navigationBarBackButtonHidden(true)
        .task {
            do {
                // Load Whisper model for transcription
                try await recorder.loadModel(variant: "small")

                // Load PII Guardian for privacy protection
                try await LLMModelManager.shared.loadModel()
            } catch {
                showError = true
            }
        }
        .alert("Error", isPresented: $showError) {
            Button("OK") { showError = false }
        } message: {
            Text(recorder.error ?? "Unknown error")
        }
        .alert("Delete Recording", isPresented: $showDeleteConfirmation) {
            Button("Cancel", role: .cancel) {
                recordingToDelete = nil
            }
            Button("Delete", role: .destructive) {
                if let recording = recordingToDelete {
                    deleteRecording(recording)
                }
            }
        } message: {
            Text("Are you sure you want to delete this recording? This action cannot be undone.")
        }
        .sheet(isPresented: $showRenameDialog) {
            NavigationStack {
                VStack(spacing: 20) {
                    Text("Rename Recording")
                        .font(.headline)
                        .padding(.top)

                    TextField("Recording name", text: $newRecordingName)
                        .textFieldStyle(.roundedBorder)
                        .padding(.horizontal)

                    Spacer()
                }
                .toolbar {
                    ToolbarItem(placement: .cancellationAction) {
                        Button("Cancel") {
                            showRenameDialog = false
                            recordingToRename = nil
                        }
                    }
                    ToolbarItem(placement: .confirmationAction) {
                        Button("Save") {
                            if let recording = recordingToRename {
                                renameRecording(recording, newName: newRecordingName)
                            }
                            showRenameDialog = false
                        }
                        .disabled(newRecordingName.isEmpty)
                    }
                }
            }
            .presentationDetents([.height(200)])
        }
    }

    // MARK: - Helper Functions

    private func formatDuration(_ duration: TimeInterval) -> String {
        let minutes = Int(duration) / 60
        let seconds = Int(duration) % 60
        return String(format: "%d:%02d", minutes, seconds)
    }

    private func deleteRecording(_ recording: Recording) {
        var updatedEvent = currentEvent
        updatedEvent.recordings.removeAll { $0.id == recording.id }

        do {
            try EventStorageManager.shared.saveEvent(updatedEvent)
            currentEvent = updatedEvent
            print("✅ Recording deleted: \(recording.id)")

            // Delete audio file if it exists
            if let audioPath = recording.audioFilePath {
                let fileManager = FileManager.default
                let documentsURL = fileManager.urls(for: .documentDirectory, in: .userDomainMask)[0]
                let audioURL = documentsURL.appendingPathComponent(audioPath)
                try? fileManager.removeItem(at: audioURL)
                print("🗑️ Audio file deleted: \(audioPath)")
            }
        } catch {
            print("❌ Error deleting recording: \(error)")
            showError = true
        }

        recordingToDelete = nil
    }

    private func renameRecording(_ recording: Recording, newName: String) {
        var updatedEvent = currentEvent
        if let index = updatedEvent.recordings.firstIndex(where: { $0.id == recording.id }) {
            updatedEvent.recordings[index].name = newName

            do {
                try EventStorageManager.shared.saveEvent(updatedEvent)
                currentEvent = updatedEvent
                print("✅ Recording renamed: \(recording.id) -> \(newName)")
            } catch {
                print("❌ Error renaming recording: \(error)")
                showError = true
            }
        }

        recordingToRename = nil
    }
}

#Preview {
    NavigationStack {
        RecordingView(event: Event(name: "Tech Conference", location: "San Francisco"), onEndEvent: {})
    }
}
