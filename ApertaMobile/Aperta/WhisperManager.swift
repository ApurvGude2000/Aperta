import Foundation
import SwiftUI
import Combine

/// Singleton manager for Whisper model lifecycle
@MainActor
class WhisperManager: ObservableObject {
    static let shared = WhisperManager()

    let recorder: SimpleWhisperRecorder
    @Published var isModelLoaded = false
    @Published var modelLoadingProgress: Double = 0
    @Published var loadingError: String? = nil

    private init() {
        self.recorder = SimpleWhisperRecorder()
    }

    /// Load model once at app startup
    func loadModelIfNeeded(variant: String = "small") async {
        // If already loaded, skip
        guard !isModelLoaded else { return }

        do {
            loadingError = nil
            modelLoadingProgress = 0

            print("Loading Whisper model...")
            try await recorder.loadModel(variant: variant)

            isModelLoaded = true
            modelLoadingProgress = 1.0
            print("Whisper model loaded successfully!")

        } catch {
            loadingError = "Failed to load model: \(error.localizedDescription)"
            print("Error loading model: \(error)")
        }
    }
}
