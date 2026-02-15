// ABOUTME: Base protocol for on-device agents
// ABOUTME: Defines agent architecture similar to backend agents

import Foundation

/// Base protocol for all agents
protocol Agent {
    /// Agent identifier
    var name: String { get }

    /// What this agent does
    var purpose: String { get }

    /// Execute the agent's task
    func execute(input: String) async -> AgentResult
}

/// Result returned by agent execution
struct AgentResult {
    /// Processed output
    let output: String

    /// Step-by-step reasoning (what the agent did)
    let reasoning: [String]

    /// Additional metadata
    let metadata: [String: Any]

    /// Whether execution was successful
    let success: Bool

    /// Optional error message
    let error: String?

    init(output: String, reasoning: [String], metadata: [String: Any] = [:], success: Bool = true, error: String? = nil) {
        self.output = output
        self.reasoning = reasoning
        self.metadata = metadata
        self.success = success
        self.error = error
    }
}

/// Represents a detected PII entity
struct PIIEntity {
    /// Type of PII (email, phone, address, etc.)
    let type: PIIType

    /// The actual text that was detected
    let value: String

    /// Range in the original string
    let range: NSRange

    /// Placeholder to use when redacting
    let placeholder: String

    /// Confidence score (0.0 - 1.0)
    let confidence: Float

    /// Redact this entity in the given text
    func redact(in text: String) -> String {
        guard let range = Range(range, in: text) else { return text }
        return text.replacingCharacters(in: range, with: placeholder)
    }
}

/// Types of PII that can be detected
enum PIIType: String, CaseIterable {
    case email = "EMAIL"
    case phone = "PHONE"
    case streetAddress = "STREET_ADDRESS"
    case city = "CITY"
    case stateProvince = "STATE_PROVINCE"
    case zipCode = "ZIP_CODE"
    case country = "COUNTRY"  // Detected but not redacted
    case creditCard = "CREDIT_CARD"
    case ssn = "SSN"
    case address = "ADDRESS"  // Generic address (from LLM)

    var displayName: String {
        switch self {
        case .email: return "Email"
        case .phone: return "Phone Number"
        case .streetAddress: return "Street Address"
        case .city: return "City"
        case .stateProvince: return "State/Province"
        case .zipCode: return "ZIP Code"
        case .country: return "Country"
        case .creditCard: return "Credit Card"
        case .ssn: return "SSN"
        case .address: return "Address"
        }
    }

    var shouldRedact: Bool {
        // Don't redact country - keep for context
        return self != .country
    }
}
