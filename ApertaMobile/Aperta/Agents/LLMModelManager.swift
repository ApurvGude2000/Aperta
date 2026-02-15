// ABOUTME: PII Guardian - Advanced pattern-based detection with optional LLM upgrade path
// ABOUTME: Fast, accurate regex-based redaction ready for production use

import Foundation
import Combine

/// PII Guardian - Detects and redacts PII using advanced pattern matching
/// Fast on-device protection with regex, designed to be upgraded to LLM inference later
@MainActor
class LLMModelManager: ObservableObject {
    static let shared = LLMModelManager()

    @Published private(set) var isModelLoaded = false
    @Published private(set) var loadingProgress: Double = 0
    @Published private(set) var loadingError: String?
    @Published var isEnabled = true // Toggle PII protection on/off

    private init() {}

    /// Load the PII detector (instant with regex-based approach)
    func loadModel() async throws {
        guard !isModelLoaded else { return }

        print("📦 Loading PII Guardian (pattern-based detection)...")
        loadingProgress = 0.5

        // Regex patterns are always available - no model loading needed
        try await Task.sleep(nanoseconds: 100_000_000) // 0.1s for smooth UX

        loadingProgress = 1.0
        isModelLoaded = true

        print("✅ PII Guardian ready")
    }

    /// Detect and redact PII from text using advanced pattern matching
    func redactPII(from text: String) async throws -> String {
        guard isEnabled else {
            print("⏭️ PII protection disabled")
            return text
        }

        guard !text.isEmpty else { return text }

        print("🛡️ Protecting text (\(text.count) chars) from PII exposure...")

        let redacted = applyAdvancedPatterns(to: text)

        let redactionCount = countRedactions(in: redacted)
        if redactionCount > 0 {
            print("✅ Protected: \(redactionCount) PII entities redacted")
        } else {
            print("✅ No PII detected")
        }

        return redacted
    }

    /// Unload model (no-op for regex-based approach)
    func unloadModel() {
        isModelLoaded = false
        print("🗑️ PII Guardian unloaded")
    }

    // MARK: - Advanced Pattern Matching

    private func applyAdvancedPatterns(to text: String) -> String {
        var result = text

        // 1. Email addresses (comprehensive pattern)
        result = redactPattern(
            in: result,
            pattern: #"(?i)\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b"#,
            replacement: "[EMAIL]"
        )

        // 2. Phone numbers (multiple formats)
        // US/Canada: (123) 456-7890, 123-456-7890, 123.456.7890, 1234567890
        result = redactPattern(
            in: result,
            pattern: #"(?:\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b"#,
            replacement: "[PHONE]"
        )

        // International: +44 20 1234 5678, +33 1 23 45 67 89
        result = redactPattern(
            in: result,
            pattern: #"\+\d{1,3}[\s.-]?\(?\d{1,4}\)?[\s.-]?\d{1,4}[\s.-]?\d{1,9}"#,
            replacement: "[PHONE]"
        )

        // 3. Social Security Numbers (US)
        result = redactPattern(
            in: result,
            pattern: #"\b\d{3}[-\s]?\d{2}[-\s]?\d{4}\b"#,
            replacement: "[SSN]"
        )

        // 4. Credit Card Numbers (Visa, MC, Amex, Discover)
        result = redactPattern(
            in: result,
            pattern: #"\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b"#,
            replacement: "[CARD]"
        )
        result = redactPattern(
            in: result,
            pattern: #"\b\d{4}[\s-]?\d{6}[\s-]?\d{5}\b"#,  // Amex: 15 digits
            replacement: "[CARD]"
        )

        // 5. Full Addresses (street patterns)
        result = redactPattern(
            in: result,
            pattern: #"\b\d+\s+[A-Z][a-z]+(\s+[A-Z][a-z]+)*\s+(Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Lane|Ln|Drive|Dr|Court|Ct)\b"#,
            replacement: "[ADDRESS]"
        )

        // 6. ZIP Codes (US)
        result = redactPattern(
            in: result,
            pattern: #"\b\d{5}(-\d{4})?\b"#,
            replacement: "[ZIP]"
        )

        // 7. IP Addresses (v4)
        result = redactPattern(
            in: result,
            pattern: #"\b(?:\d{1,3}\.){3}\d{1,3}\b"#,
            replacement: "[IP]"
        )

        // 8. Passport Numbers (US format: Letter + 8 digits)
        result = redactPattern(
            in: result,
            pattern: #"\b[A-Z]\d{8}\b"#,
            replacement: "[PASSPORT]"
        )

        return result
    }

    private func redactPattern(in text: String, pattern: String, replacement: String) -> String {
        guard let regex = try? NSRegularExpression(pattern: pattern, options: []) else {
            return text
        }

        let range = NSRange(text.startIndex..., in: text)
        return regex.stringByReplacingMatches(
            in: text,
            options: [],
            range: range,
            withTemplate: replacement
        )
    }

    private func countRedactions(in text: String) -> Int {
        let redactionTokens = ["[EMAIL]", "[PHONE]", "[SSN]", "[CARD]", "[ADDRESS]", "[ZIP]", "[IP]", "[PASSPORT]"]
        return redactionTokens.reduce(0) { count, token in
            count + text.components(separatedBy: token).count - 1
        }
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
            return "PII Guardian not loaded. Call loadModel() first."
        case .modelNotFound:
            return "Model file not found."
        case .modelLoadFailed:
            return "Failed to load model file."
        case .contextCreationFailed:
            return "Failed to create context."
        case .generationFailed(let reason):
            return "Detection failed: \(reason)"
        }
    }
}
