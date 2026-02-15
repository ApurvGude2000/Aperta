// ABOUTME: Integration example showing how to use PII Guardian Agent
// ABOUTME: Call this after transcription completes to protect PII before storage/upload

import Foundation

/// Manager for PII protection in the recording flow
class PIIProtectionManager {
    static let shared = PIIProtectionManager()

    private let guardian = PIIGuardianAgent()

    /// Process transcript with PII protection
    func protectTranscript(_ transcript: String) async -> ProtectedTranscript {
        let result = await guardian.execute(input: transcript)

        return ProtectedTranscript(
            original: transcript,
            redacted: result.output,
            reasoning: result.reasoning,
            metadata: result.metadata,
            wasRedacted: result.metadata["redacted"] as? Bool ?? false
        )
    }

    /// Quick check if PII protection is needed
    func needsProtection(_ transcript: String) async -> Bool {
        return await guardian.containsPII(transcript)
    }

    /// Analyze PII without redacting (for UI preview)
    func analyzeForUI(_ transcript: String) async -> PIIAnalysis {
        return await guardian.analyzePII(transcript)
    }
}

/// Protected transcript with both versions
struct ProtectedTranscript {
    /// Original unredacted transcript (store encrypted locally only)
    let original: String

    /// Redacted transcript (safe to upload to backend)
    let redacted: String

    /// Agent's reasoning steps
    let reasoning: [String]

    /// Metadata about redaction
    let metadata: [String: Any]

    /// Whether any PII was redacted
    let wasRedacted: Bool

    /// Summary for UI display
    var summary: String {
        if !wasRedacted {
            return "✅ No PII detected"
        }

        let count = metadata["pii_count"] as? Int ?? 0
        let types = metadata["types_found"] as? [String] ?? []
        return "🛡️ Protected: \(count) PII entities (\(types.joined(separator: ", ")))"
    }
}

// MARK: - Usage Example in RecordingView

/*

 // After transcription completes:

 let transcript = recorder.transcriptionText

 // Protect PII on-device
 let protected = await PIIProtectionManager.shared.protectTranscript(transcript)

 // Show agent reasoning (optional, for debugging/demo)
 print("🛡️ PII Guardian Agent:")
 for step in protected.reasoning {
     print(step)
 }

 // Display summary to user
 print(protected.summary)

 // Save to storage:
 // - Original: encrypted locally (for user's eyes only)
 // - Redacted: safe to upload to backend

 let recording = Recording(
     transcript: protected.redacted,  // Use redacted version
     originalTranscript: protected.original,  // Store encrypted
     protectionApplied: protected.wasRedacted
 )

 // Upload to backend - only redacted version leaves device
 uploadToBackend(protected.redacted)

 */

// MARK: - UI Integration Example

extension ProtectedTranscript {
    /// Format reasoning for display in UI
    var formattedReasoning: String {
        reasoning.joined(separator: "\n")
    }

    /// Get redaction statistics for UI
    var stats: PIIStats {
        let count = metadata["pii_count"] as? Int ?? 0
        let typesSummary = metadata["types_summary"] as? [String] ?? []

        return PIIStats(
            totalRedacted: count,
            breakdown: typesSummary,
            wasProtected: wasRedacted
        )
    }
}

struct PIIStats {
    let totalRedacted: Int
    let breakdown: [String]
    let wasProtected: Bool

    var displayText: String {
        if !wasProtected {
            return "No sensitive information detected"
        }

        var text = "Protected \(totalRedacted) sensitive item\(totalRedacted == 1 ? "" : "s")"
        if !breakdown.isEmpty {
            text += ":\n" + breakdown.map { "• \($0)" }.joined(separator: "\n")
        }
        return text
    }
}
