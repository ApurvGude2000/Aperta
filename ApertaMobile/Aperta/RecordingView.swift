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
            // Event info at top
            VStack(spacing: 4) {
                Text(event.name)
                    .font(.title2)
                    .bold()
                HStack {
                    Image(systemName: "location.fill")
                        .font(.caption)
                    Text(event.location)
                        .font(.subheadline)
                        .foregroundColor(.gray)
                }
            }
            .padding(.top)
            
            // Model loading indicator
            if !recorder.isModelLoaded {
                VStack {
                    Text("Loading Whisper Model...")
                    ProgressView(value: recorder.modelLoadingProgress)
                        .padding()
                }
            }

            // Recording status with timer and indicator
            if recorder.isRecording {
                HStack(spacing: 12) {
                    PulsingRecordIndicator(isRecording: recorder.isRecording)
                    RecordingTimerView(duration: recorder.recordingDuration)
                }
                .padding(.vertical, 8)
            }

            // Visual feedback during recording
            if recorder.isRecording {
                VStack(spacing: 16) {
                    // Waveform visualization
                    WaveformView(level: recorder.audioLevel)
                        .frame(height: 80)
                        .padding(.horizontal)

                    // Audio level meter
                    HStack {
                        Image(systemName: "speaker.wave.2.fill")
                            .font(.caption)
                            .foregroundColor(.gray)
                        AudioLevelMeter(level: recorder.audioLevel)
                    }
                }
                .padding(.vertical)
                .background(Color.gray.opacity(0.05))
                .cornerRadius(12)
                .padding(.horizontal)
            }
            
            // Live transcript display
            ScrollView {
                Text(recorder.transcriptionText.isEmpty ? "Press record and speak..." : recorder.transcriptionText)
                    .padding()
                    .frame(maxWidth: .infinity, alignment: .leading)
                    .background(Color.gray.opacity(0.1))
                    .cornerRadius(10)
            }
            .frame(height: 300)
            
            // Recording controls
            VStack(spacing: 12) {
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
                        .padding()
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
                            .padding()
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
                            .padding()
                            .background(Color.red)
                            .foregroundColor(.white)
                            .cornerRadius(10)
                        }
                    }
                }

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
            
            if recorder.isTranscribing {
                HStack {
                    ProgressView()
                    Text("Transcribing...")
                }
            }
            
            Spacer()
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
