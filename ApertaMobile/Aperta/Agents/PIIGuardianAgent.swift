// ABOUTME: PII Guardian Agent for on-device privacy protection
// ABOUTME: Detects and redacts emails, addresses, and phone numbers while preserving names

import Foundation

/// On-device PII detection and redaction agent
/// Protects privacy by redacting sensitive information before upload
class PIIGuardianAgent: Agent {
    let name = "PII Guardian"
    let purpose = "Detect and redact PII (emails, addresses, phone numbers) before data leaves device"

    // Detection tools - in order of execution
    private let tools: [PIIDetectionTool] = [
        EmailDetector(),
        PhoneDetector(),
        StreetAddressDetector(),
        CityDetector(),
        StateProvinceDetector(),
        ZipCodeDetector()
    ]

    /// Execute PII detection and redaction
    func execute(input: String) async -> AgentResult {
        var redactedText = input
        var reasoning: [String] = []
        var allEntities: [PIIEntity] = []

        reasoning.append("🛡️ Starting PII scan...")

        // Step 1: Detect all PII entities
        for tool in tools {
            let entities = tool.detect(in: input)

            if !entities.isEmpty {
                let typeDisplay = entities.first?.type.displayName ?? "Unknown"
                reasoning.append("✓ Found \(entities.count) \(typeDisplay)\(entities.count == 1 ? "" : "s")")

                // Only keep entities that should be redacted
                let toRedact = entities.filter { $0.type.shouldRedact }
                allEntities.append(contentsOf: toRedact)

                // Log if some were skipped
                let skipped = entities.count - toRedact.count
                if skipped > 0 {
                    reasoning.append("  ℹ️ Keeping \(skipped) for context")
                }
            }
        }

        if allEntities.isEmpty {
            reasoning.append("✅ No PII detected - transcript is clean")
            return AgentResult(
                output: input,
                reasoning: reasoning,
                metadata: [
                    "pii_count": 0,
                    "types_found": [],
                    "redacted": false
                ]
            )
        }

        // Step 2: Sort entities by range (longest first to avoid nested issues)
        let sortedEntities = allEntities.sorted { entity1, entity2 in
            // Sort by position (earlier first), then by length (longer first)
            if entity1.range.location == entity2.range.location {
                return entity1.range.length > entity2.range.length
            }
            return entity1.range.location < entity2.range.location
        }

        // Step 3: Redact from back to front to maintain range validity
        let reversedEntities = sortedEntities.reversed()
        var nsText = redactedText as NSString

        for entity in reversedEntities {
            let value = nsText.substring(with: entity.range)
            reasoning.append("→ Redacting \(entity.type.displayName): '\(truncate(value, maxLength: 30))' → '\(entity.placeholder)'")

            // Perform redaction
            if let range = Range(entity.range, in: redactedText) {
                redactedText.replaceSubrange(range, with: entity.placeholder)
                nsText = redactedText as NSString
            }
        }

        reasoning.append("✅ Protection complete! \(allEntities.count) PII entities redacted")

        // Step 4: Gather statistics
        let typesSummary = Dictionary(grouping: allEntities, by: { $0.type })
            .mapValues { $0.count }
            .sorted { $0.key.displayName < $1.key.displayName }

        return AgentResult(
            output: redactedText,
            reasoning: reasoning,
            metadata: [
                "pii_count": allEntities.count,
                "types_found": Array(Set(allEntities.map { $0.type.rawValue })).sorted(),
                "types_summary": typesSummary.map { "\($0.key.displayName): \($0.value)" },
                "redacted": true,
                "original_length": input.count,
                "redacted_length": redactedText.count
            ]
        )
    }

    /// Truncate long strings for logging
    private func truncate(_ text: String, maxLength: Int) -> String {
        if text.count <= maxLength {
            return text
        }
        let prefix = text.prefix(maxLength - 3)
        return "\(prefix)..."
    }
}

// MARK: - Convenience Extensions

extension PIIGuardianAgent {
    /// Quick check if text contains PII without redacting
    func containsPII(_ text: String) async -> Bool {
        for tool in tools {
            let entities = tool.detect(in: text).filter { $0.type.shouldRedact }
            if !entities.isEmpty {
                return true
            }
        }
        return false
    }

    /// Get summary of PII found without redacting
    func analyzePII(_ text: String) async -> PIIAnalysis {
        var entityCounts: [PIIType: Int] = [:]

        for tool in tools {
            let entities = tool.detect(in: text).filter { $0.type.shouldRedact }
            if !entities.isEmpty {
                entityCounts[tool.entityType] = entities.count
            }
        }

        return PIIAnalysis(
            containsPII: !entityCounts.isEmpty,
            totalCount: entityCounts.values.reduce(0, +),
            breakdown: entityCounts
        )
    }
}

/// Analysis result for PII detection
struct PIIAnalysis {
    let containsPII: Bool
    let totalCount: Int
    let breakdown: [PIIType: Int]

    var summary: String {
        if !containsPII {
            return "No PII detected"
        }

        let items = breakdown.map { "\($0.key.displayName): \($0.value)" }.joined(separator: ", ")
        return "\(totalCount) PII entities found (\(items))"
    }
}
