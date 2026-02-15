import SwiftUI

struct LoadingView: View {
    @StateObject private var whisperManager = WhisperManager.shared
    @State private var isReady = false
    
    var body: some View {
        Group {
            if isReady {
                EventCreationView()
            } else {
                VStack(spacing: 24) {
                    Spacer()

                    // Aperta Logo
                    Image("aperta-logo")
                        .resizable()
                        .scaledToFit()
                        .frame(width: 120, height: 120)

                    VStack(spacing: 4) {
                        Text("Agent Echo")
                            .font(.title)
                            .bold()
                        Text("by Aperta")
                            .font(.title3)
                            .foregroundColor(.gray)
                    }

                    Spacer()
                    
                    VStack(spacing: 16) {
                        ProgressView(value: whisperManager.modelLoadingProgress)
                            .progressViewStyle(.linear)
                            .frame(width: 200)
                        
                        Text("Loading Whisper model...")
                            .font(.headline)
                        
                        Text("This only happens once")
                            .font(.caption)
                            .foregroundColor(.gray)
                    }
                    
                    if let error = whisperManager.loadingError {
                        Text(error)
                            .foregroundColor(.red)
                            .font(.caption)
                            .padding()
                    }
                    
                    Spacer()
                }
                .padding()
                .task {
                    await whisperManager.loadModelIfNeeded(variant: "small")
                    // Wait a moment to ensure everything is ready
                    try? await Task.sleep(nanoseconds: 500_000_000)
                    isReady = true
                }
            }
        }
    }
}

#Preview {
    LoadingView()
}
