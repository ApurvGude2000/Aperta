import SwiftUI

struct RecordingView: View {
    let event: Event
    let onEndEvent: () -> Void
    @StateObject private var recorder = SimpleWhisperRecorder()
    @State private var showError = false
    @State private var hasRecordedOnce = false
    @Environment(\.dismiss) private var dismiss
    
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

                    if !event.recordings.isEmpty {
                        HStack(spacing: 4) {
                            Image(systemName: "waveform.circle.fill")
                                .font(.caption)
                            Text("\(event.recordings.count) recording\(event.recordings.count == 1 ? "" : "s")")
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
                                        try await recorder.stopRecordingAndTranscribe()
                                        hasRecordedOnce = true
                                    } catch {
                                        showError = true
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
            
            if recorder.isTranscribing {
                HStack {
                    ProgressView()
                    Text("Transcribing...")
                }
            }
        }
        .padding()
        .navigationBarBackButtonHidden(true)
        .task {
            do {
                try await recorder.loadModel(variant: "small")
            } catch {
                showError = true
            }
        }
        .alert("Error", isPresented: $showError) {
            Button("OK") { showError = false }
        } message: {
            Text(recorder.error ?? "Unknown error")
        }
    }
}

#Preview {
    NavigationStack {
        RecordingView(event: Event(name: "Tech Conference", location: "San Francisco"), onEndEvent: {})
    }
}
