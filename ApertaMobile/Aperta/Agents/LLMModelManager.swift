// ABOUTME: Manager for on-device LLM (Llama 3.2 1B) - Stub implementation
// ABOUTME: TODO: Implement with working MLX Swift integration

import Foundation
import Combine

/// Manages the on-device LLM for PII detection
/// STUB: Currently returns placeholder responses until MLX integration is working
@MainActor
class LLMModelManager: ObservableObject {
    static let shared = LLMModelManager()

    @Published private(set) var isModelLoaded = false
    @Published private(set) var loadingProgress: Double = 0
    @Published private(set) var loadingError: String?

    private init() {}

    /// Load the LLM model (call once at app startup)
    func loadModel() async throws {
        guard !isModelLoaded else { return }

        print("📦 Loading stub LLM (MLX integration pending)...")

        // Simulate loading
        loadingProgress = 0.5
        try await Task.sleep(nanoseconds: 500_000_000) // 0.5s

        loadingProgress = 1.0
        isModelLoaded = true

        print("✅ Stub LLM loaded (TODO: Replace with real MLX implementation)")
    }

    /// Generate text with the LLM for PII detection
    /// STUB: Returns a simple regex-based redaction for now
    func generate(prompt: String, maxTokens: Int = 300) async throws -> String {
        guard isModelLoaded else {
            throw LLMError.modelNotLoaded
        }

        print("🔍 Stub PII detection (TODO: Use real LLM)")

        // Extract the text to redact from the prompt
        let text = extractTextFromPrompt(prompt)

        // Simple regex-based redaction as placeholder
        var redacted = text

        // Redact emails
        redacted = redacted.replacingOccurrences(
            of: #"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"#,
            with: "[EMAIL]",
            options: .regularExpression
        )

        // Redact phone numbers (simple pattern)
        redacted = redacted.replacingOccurrences(
            of: #"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b"#,
            with: "[PHONE]",
            options: .regularExpression
        )

        // Redact SSN-like patterns
        redacted = redacted.replacingOccurrences(
            of: #"\b\d{3}-\d{2}-\d{4}\b"#,
            with: "[SSN]",
            options: .regularExpression
        )

        // Redact credit card patterns
        redacted = redacted.replacingOccurrences(
            of: #"\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b"#,
            with: "[CARD]",
            options: .regularExpression
        )

        print("✅ Stub redaction complete")
        return redacted
    }

    /// Unload model to free memory
    func unloadModel() {
        isModelLoaded = false
        print("🗑️ Stub model unloaded")
    }

    // MARK: - Helper Methods

    private func extractTextFromPrompt(_ prompt: String) -> String {
        // Extract text between "Redact PII from this text:" and "<|eot_id|>"
        if let range = prompt.range(of: "Redact PII from this text:\n") {
            let startIndex = range.upperBound
            if let endRange = prompt[startIndex...].range(of: "<|eot_id|>") {
                return String(prompt[startIndex..<endRange.lowerBound])
            }
            return String(prompt[startIndex...])
        }
        // Fallback: return the whole prompt
        return prompt
    }
}

// MARK: - Errors

enum LLMError: LocalizedError {
    case modelNotLoaded
    case modelNotFound
    case modelLoadFailed
    case contextCreationFailed
    case generationFailed(String)

    var errorDescription: String? {
        switch self {
        case .modelNotLoaded:
            return "LLM model not loaded. Call loadModel() first."
        case .modelNotFound:
            return "Model file not found."
        case .modelLoadFailed:
            return "Failed to load model file."
        case .contextCreationFailed:
            return "Failed to create LLM context."
        case .generationFailed(let reason):
            return "Text generation failed: \(reason)"
        }
    }
}
