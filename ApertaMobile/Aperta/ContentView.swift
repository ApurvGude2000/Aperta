import SwiftUI

struct ContentView: View {
    @StateObject private var recorder = SimpleWhisperRecorder()
    @State private var showError = false

    var body: some View {
        VStack(spacing: 20) {
            Text("Aperta")
                .font(.largeTitle)
                .bold()

            if !recorder.isModelLoaded {
                VStack {
                    Text("Loading Model...")
                    ProgressView(value: recorder.modelLoadingProgress)
                        .padding()
                }
            }

            ScrollView {
                Text(recorder.transcriptionText.isEmpty ? "Press record and speak..." : recorder.transcriptionText)
                    .padding()
                    .frame(maxWidth: .infinity, alignment: .leading)
                    .background(Color.gray.opacity(0.1))
                    .cornerRadius(10)
            }
            .frame(height: 300)

            Button(action: {
                Task {
                    do {
                        if recorder.isRecording {
                            try await recorder.stopRecordingAndTranscribe()
                        } else {
                            try await recorder.startRecording()
                        }
                    } catch {
                        showError = true
                    }
                }
            }) {
                HStack {
                    Image(systemName: recorder.isRecording ? "stop.circle.fill" : "mic.circle.fill")
                        .font(.title)
                    Text(recorder.isRecording ? "Stop & Transcribe" : "Start Recording")
                }
                .frame(maxWidth: .infinity)
                .padding()
                .background(recorder.isRecording ? Color.red : Color.blue)
                .foregroundColor(.white)
                .cornerRadius(10)
            }
            .disabled(!recorder.isModelLoaded || recorder.isTranscribing)

            if recorder.isTranscribing {
                HStack {
                    ProgressView()
                    Text("Transcribing...")
                }
            }

            Spacer()
        }
        .padding()
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
    ContentView()
}
