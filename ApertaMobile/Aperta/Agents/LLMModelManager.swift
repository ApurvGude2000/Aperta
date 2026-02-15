// ABOUTME: Manager for on-device LLM (Llama 3.2 1B) using MLX Swift
// ABOUTME: Handles model loading, caching, and inference for PII detection

import Foundation
import MLX
import MLXRandom
import MLXNN
import MLXOptimizers
import MLXLM

/// Manages the on-device LLM for PII detection
@MainActor
class LLMModelManager: ObservableObject {
    static let shared = LLMModelManager()

    @Published private(set) var isModelLoaded = false
    @Published private(set) var loadingProgress: Double = 0
    @Published private(set) var loadingError: String?

    private var modelContainer: ModelContainer?
    private let modelName = "mlx-community/Llama-3.2-1B-Instruct-4bit"

    private init() {}

    /// Load the LLM model (call once at app startup)
    func loadModel() async throws {
        guard !isModelLoaded else { return }

        do {
            loadingProgress = 0.0
            loadingError = nil

            print("📦 Loading Llama 3.2 1B model...")

            // Load model with 4-bit quantization for speed
            modelContainer = try await ModelContainer.load(
                hub: .init(repo: modelName),
                configuration: .init(
                    id: modelName,
                    defaultPrompt: ""
                )
            ) { progress in
                Task { @MainActor in
                    self.loadingProgress = progress.fractionCompleted
                    print("📦 Model loading: \(Int(progress.fractionCompleted * 100))%")
                }
            }

            isModelLoaded = true
            print("✅ Llama 3.2 1B loaded successfully")

        } catch {
            loadingError = "Failed to load model: \(error.localizedDescription)"
            print("❌ Model loading failed: \(error)")
            throw error
        }
    }

    /// Generate text with the LLM
    func generate(prompt: String, maxTokens: Int = 512) async throws -> String {
        guard let container = modelContainer else {
            throw LLMError.modelNotLoaded
        }

        do {
            // Generate response
            let result = try await container.perform { model, tokenizer in
                // Tokenize prompt
                let promptTokens = tokenizer.encode(text: prompt)

                // Generate with sampling
                let output = try MLXLMCommon.generate(
                    promptTokens: promptTokens,
                    parameters: .init(
                        temperature: 0.1,  // Low temperature for consistent PII detection
                        topP: 0.9,
                        maxTokens: maxTokens
                    ),
                    model: model,
                    tokenizer: tokenizer
                ) { tokens in
                    // Progress callback (optional)
                    return .more
                }

                // Decode tokens to text
                return tokenizer.decode(tokens: output)
            }

            return result

        } catch {
            print("❌ Generation failed: \(error)")
            throw LLMError.generationFailed(error.localizedDescription)
        }
    }

    /// Unload model to free memory
    func unloadModel() {
        modelContainer = nil
        isModelLoaded = false
        print("🗑️ Model unloaded")
    }
}

// MARK: - Errors

enum LLMError: LocalizedError {
    case modelNotLoaded
    case generationFailed(String)

    var errorDescription: String? {
        switch self {
        case .modelNotLoaded:
            return "LLM model not loaded. Call loadModel() first."
        case .generationFailed(let reason):
            return "Text generation failed: \(reason)"
        }
    }
}
