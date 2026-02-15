// ABOUTME: Detection tools for identifying PII in text
// ABOUTME: Each tool specializes in detecting one type of PII entity

import Foundation

/// Protocol for PII detection tools
protocol PIIDetectionTool {
    var entityType: PIIType { get }
    func detect(in text: String) -> [PIIEntity]
}

// MARK: - Email Detector

class EmailDetector: PIIDetectionTool {
    let entityType: PIIType = .email

    func detect(in text: String) -> [PIIEntity] {
        var entities: [PIIEntity] = []

        // Email regex pattern
        let pattern = #"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"#

        guard let regex = try? NSRegularExpression(pattern: pattern, options: []) else {
            return entities
        }

        let nsText = text as NSString
        let matches = regex.matches(in: text, options: [], range: NSRange(location: 0, length: nsText.length))

        for (index, match) in matches.enumerated() {
            let value = nsText.substring(with: match.range)
            entities.append(PIIEntity(
                type: .email,
                value: value,
                range: match.range,
                placeholder: "[EMAIL_\(index + 1)]",
                confidence: 0.95
            ))
        }

        return entities
    }
}

// MARK: - Phone Number Detector

class PhoneDetector: PIIDetectionTool {
    let entityType: PIIType = .phone

    func detect(in text: String) -> [PIIEntity] {
        var entities: [PIIEntity] = []

        // Phone number patterns (US format, but extensible)
        let patterns = [
            #"\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b"#,  // 123-456-7890 or 123.456.7890 or 123 456 7890
            #"\(\d{3}\)\s?\d{3}[-.\s]?\d{4}\b"#,     // (123) 456-7890
            #"\+\d{1,3}\s?\d{3,4}[-.\s]?\d{3,4}[-.\s]?\d{4}\b"#,  // +1 123-456-7890
            #"\b\d{10}\b"#  // 1234567890
        ]

        for pattern in patterns {
            guard let regex = try? NSRegularExpression(pattern: pattern, options: []) else {
                continue
            }

            let nsText = text as NSString
            let matches = regex.matches(in: text, options: [], range: NSRange(location: 0, length: nsText.length))

            for (index, match) in matches.enumerated() {
                let value = nsText.substring(with: match.range)
                // Check if it looks like a phone number (not a random 10 digits)
                if isLikelyPhoneNumber(value) {
                    entities.append(PIIEntity(
                        type: .phone,
                        value: value,
                        range: match.range,
                        placeholder: "[PHONE_\(entities.count + 1)]",
                        confidence: 0.90
                    ))
                }
            }
        }

        // Remove duplicates (same range)
        return removeDuplicates(entities)
    }

    private func isLikelyPhoneNumber(_ text: String) -> Bool {
        // Remove non-digits
        let digits = text.filter { $0.isNumber }
        // Phone numbers are typically 10-11 digits
        return digits.count >= 10 && digits.count <= 15
    }

    private func removeDuplicates(_ entities: [PIIEntity]) -> [PIIEntity] {
        var seen = Set<NSRange>()
        return entities.filter { entity in
            if seen.contains(entity.range) {
                return false
            }
            seen.insert(entity.range)
            return true
        }
    }
}

// MARK: - Street Address Detector

class StreetAddressDetector: PIIDetectionTool {
    let entityType: PIIType = .streetAddress

    func detect(in text: String) -> [PIIEntity] {
        var entities: [PIIEntity] = []

        // Street address patterns
        let patterns = [
            // Matches: "123 Main St", "456 Oak Avenue", etc.
            #"\b\d+\s+[A-Z][a-z]+(\s+[A-Z][a-z]+)*\s+(Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Lane|Ln|Drive|Dr|Court|Ct|Circle|Cir|Way|Place|Pl)\b"#,
            // Matches: "123 Main St.", "456 Oak Ave.", etc. (with period)
            #"\b\d+\s+[A-Z][a-z]+(\s+[A-Z][a-z]+)*\s+(Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Lane|Ln|Drive|Dr|Court|Ct|Circle|Cir|Way|Place|Pl)\."#,
        ]

        for pattern in patterns {
            guard let regex = try? NSRegularExpression(pattern: pattern, options: []) else {
                continue
            }

            let nsText = text as NSString
            let matches = regex.matches(in: text, options: [], range: NSRange(location: 0, length: nsText.length))

            for (index, match) in matches.enumerated() {
                let value = nsText.substring(with: match.range)
                entities.append(PIIEntity(
                    type: .streetAddress,
                    value: value,
                    range: match.range,
                    placeholder: "[STREET_ADDRESS_\(entities.count + 1)]",
                    confidence: 0.85
                ))
            }
        }

        return entities
    }
}

// MARK: - ZIP Code Detector

class ZipCodeDetector: PIIDetectionTool {
    let entityType: PIIType = .zipCode

    func detect(in text: String) -> [PIIEntity] {
        var entities: [PIIEntity] = []

        // ZIP code patterns
        let patterns = [
            #"\b\d{5}\b"#,           // 12345
            #"\b\d{5}-\d{4}\b"#      // 12345-6789
        ]

        for pattern in patterns {
            guard let regex = try? NSRegularExpression(pattern: pattern, options: []) else {
                continue
            }

            let nsText = text as NSString
            let matches = regex.matches(in: text, options: [], range: NSRange(location: 0, length: nsText.length))

            for (index, match) in matches.enumerated() {
                let value = nsText.substring(with: match.range)
                entities.append(PIIEntity(
                    type: .zipCode,
                    value: value,
                    range: match.range,
                    placeholder: "[ZIP_\(entities.count + 1)]",
                    confidence: 0.80
                ))
            }
        }

        return entities
    }
}

// MARK: - City Detector (Simple Pattern-Based)

class CityDetector: PIIDetectionTool {
    let entityType: PIIType = .city

    // Common US cities for pattern matching
    private let commonCities = [
        "New York", "Los Angeles", "Chicago", "Houston", "Phoenix", "Philadelphia",
        "San Antonio", "San Diego", "Dallas", "San Jose", "Austin", "Jacksonville",
        "Fort Worth", "Columbus", "Charlotte", "San Francisco", "Indianapolis",
        "Seattle", "Denver", "Washington", "Boston", "Nashville", "Baltimore",
        "Oklahoma City", "Portland", "Las Vegas", "Detroit", "Memphis", "Louisville",
        "Milwaukee", "Albuquerque", "Tucson", "Fresno", "Sacramento", "Kansas City",
        "Atlanta", "Miami", "Oakland", "Minneapolis", "Tulsa", "Cleveland",
        "New Orleans", "Arlington", "Tampa", "Pittsburgh", "Cincinnati", "Orlando"
    ]

    func detect(in text: String) -> [PIIEntity] {
        var entities: [PIIEntity] = []

        for city in commonCities {
            // Case-insensitive search
            var searchRange = text.startIndex..<text.endIndex
            while let range = text.range(of: city, options: [.caseInsensitive], range: searchRange) {
                let nsRange = NSRange(range, in: text)
                entities.append(PIIEntity(
                    type: .city,
                    value: String(text[range]),
                    range: nsRange,
                    placeholder: "[CITY_\(entities.count + 1)]",
                    confidence: 0.75
                ))

                // Continue searching after this match
                searchRange = range.upperBound..<text.endIndex
            }
        }

        return entities
    }
}

// MARK: - State/Province Detector

class StateProvinceDetector: PIIDetectionTool {
    let entityType: PIIType = .stateProvince

    // US state abbreviations and full names
    private let usStates = [
        "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA",
        "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD",
        "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ",
        "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC",
        "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY",
        "Alabama", "Alaska", "Arizona", "Arkansas", "California", "Colorado",
        "Connecticut", "Delaware", "Florida", "Georgia", "Hawaii", "Idaho",
        "Illinois", "Indiana", "Iowa", "Kansas", "Kentucky", "Louisiana",
        "Maine", "Maryland", "Massachusetts", "Michigan", "Minnesota",
        "Mississippi", "Missouri", "Montana", "Nebraska", "Nevada",
        "New Hampshire", "New Jersey", "New Mexico", "New York",
        "North Carolina", "North Dakota", "Ohio", "Oklahoma", "Oregon",
        "Pennsylvania", "Rhode Island", "South Carolina", "South Dakota",
        "Tennessee", "Texas", "Utah", "Vermont", "Virginia", "Washington",
        "West Virginia", "Wisconsin", "Wyoming"
    ]

    func detect(in text: String) -> [PIIEntity] {
        var entities: [PIIEntity] = []

        for state in usStates {
            // Word boundary pattern to avoid false matches
            let pattern = "\\b\(state)\\b"
            guard let regex = try? NSRegularExpression(pattern: pattern, options: []) else {
                continue
            }

            let nsText = text as NSString
            let matches = regex.matches(in: text, options: [], range: NSRange(location: 0, length: nsText.length))

            for match in matches {
                let value = nsText.substring(with: match.range)
                entities.append(PIIEntity(
                    type: .stateProvince,
                    value: value,
                    range: match.range,
                    placeholder: "[STATE_\(entities.count + 1)]",
                    confidence: 0.80
                ))
            }
        }

        return entities
    }
}

// MARK: - Credit Card Detector

class CreditCardDetector: PIIDetectionTool {
    let entityType: PIIType = .creditCard

    func detect(in text: String) -> [PIIEntity] {
        var entities: [PIIEntity] = []

        // Credit card patterns (Visa, Mastercard, Amex, Discover)
        let patterns = [
            #"\b4\d{3}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b"#,  // Visa
            #"\b5[1-5]\d{2}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b"#,  // Mastercard
            #"\b3[47]\d{2}[-\s]?\d{6}[-\s]?\d{5}\b"#,  // Amex
            #"\b6011[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b"#,  // Discover
            #"\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b"#  // Generic 16-digit
        ]

        for pattern in patterns {
            guard let regex = try? NSRegularExpression(pattern: pattern, options: []) else {
                continue
            }

            let nsText = text as NSString
            let matches = regex.matches(in: text, options: [], range: NSRange(location: 0, length: nsText.length))

            for match in matches {
                let value = nsText.substring(with: match.range)
                // Verify with Luhn algorithm (optional but recommended)
                if passesLuhnCheck(value) {
                    entities.append(PIIEntity(
                        type: .creditCard,
                        value: value,
                        range: match.range,
                        placeholder: "[CREDIT_CARD_\(entities.count + 1)]",
                        confidence: 0.95
                    ))
                }
            }
        }

        return entities
    }

    /// Luhn algorithm to validate credit card numbers
    private func passesLuhnCheck(_ number: String) -> Bool {
        let digits = number.filter { $0.isNumber }
        guard digits.count >= 13 && digits.count <= 19 else { return false }

        let reversed = digits.reversed().map { Int(String($0)) ?? 0 }
        var sum = 0

        for (index, digit) in reversed.enumerated() {
            if index % 2 == 1 {
                let doubled = digit * 2
                sum += doubled > 9 ? doubled - 9 : doubled
            } else {
                sum += digit
            }
        }

        return sum % 10 == 0
    }
}

// MARK: - SSN Detector

class SSNDetector: PIIDetectionTool {
    let entityType: PIIType = .ssn

    func detect(in text: String) -> [PIIEntity] {
        var entities: [PIIEntity] = []

        // SSN patterns (US Social Security Number)
        let patterns = [
            #"\b\d{3}-\d{2}-\d{4}\b"#,  // 123-45-6789
            #"\b\d{3}\s\d{2}\s\d{4}\b"#  // 123 45 6789
        ]

        for pattern in patterns {
            guard let regex = try? NSRegularExpression(pattern: pattern, options: []) else {
                continue
            }

            let nsText = text as NSString
            let matches = regex.matches(in: text, options: [], range: NSRange(location: 0, length: nsText.length))

            for match in matches {
                let value = nsText.substring(with: match.range)
                entities.append(PIIEntity(
                    type: .ssn,
                    value: value,
                    range: match.range,
                    placeholder: "[SSN_\(entities.count + 1)]",
                    confidence: 0.95
                ))
            }
        }

        return entities
    }
}

// Helper extension
extension NSRange: Hashable {
    public func hash(into hasher: inout Hasher) {
        hasher.combine(location)
        hasher.combine(length)
    }
}
