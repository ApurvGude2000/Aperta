# PII Guardian Agent - On-Device Privacy Protection

## Overview

The **PII Guardian Agent** is an on-device agent that detects and redacts personally identifiable information (PII) from transcripts **before they leave the device**. This ensures privacy protection at the source, not just at the backend.

## Architecture

```
┌─────────────────────────────────────────────┐
│          PII Guardian Agent                 │
│                                             │
│  ┌──────────────────────────────────────┐  │
│  │       Detection Tools                │  │
│  │  • EmailDetector                     │  │
│  │  • PhoneDetector                     │  │
│  │  • StreetAddressDetector             │  │
│  │  • CityDetector                      │  │
│  │  • StateProvinceDetector             │  │
│  │  • ZipCodeDetector                   │  │
│  └──────────────────────────────────────┘  │
│                                             │
│  ┌──────────────────────────────────────┐  │
│  │    Agent Orchestration               │  │
│  │  1. Scan with all tools              │  │
│  │  2. Collect entities                 │  │
│  │  3. Filter (keep names/countries)    │  │
│  │  4. Redact in order                  │  │
│  │  5. Return result + reasoning        │  │
│  └──────────────────────────────────────┘  │
└─────────────────────────────────────────────┘
```

## What Gets Redacted

✅ **Redacted (Removed):**
- Email addresses: `john@example.com` → `[EMAIL_1]`
- Phone numbers: `(555) 123-4567` → `[PHONE_1]`
- Street addresses: `123 Main St` → `[STREET_ADDRESS_1]`
- Cities: `San Francisco` → `[CITY_1]`
- States/Provinces: `California` → `[STATE_1]`
- ZIP codes: `94102` → `[ZIP_1]`

❌ **Kept (Preserved for Context):**
- Person names: `"I met Sarah Smith"` → stays as-is
- Organization names: `"She works at Google"` → stays as-is
- Countries: `"I'm visiting from Canada"` → stays as-is

## Why Keep Names?

This is a **networking app** - knowing WHO you talked to is essential! We protect contact details but preserve networking context.

## Usage

### Basic Usage

```swift
// After transcription
let transcript = recorder.transcriptionText

// Protect with PII Guardian
let protected = await PIIProtectionManager.shared.protectTranscript(transcript)

// Use redacted version for upload
uploadToBackend(protected.redacted)

// Store original encrypted locally (optional)
saveEncrypted(protected.original)
```

### Check for PII Before Processing

```swift
let needsProtection = await PIIProtectionManager.shared.needsProtection(transcript)

if needsProtection {
    print("⚠️ PII detected - protection recommended")
}
```

### Analyze for UI Preview

```swift
let analysis = await PIIProtectionManager.shared.analyzeForUI(transcript)
print(analysis.summary)
// Output: "3 PII entities found (Email: 1, Phone: 2)"
```

## Integration in Recording Flow

```swift
// In RecordingView or wherever transcription completes:

Task {
    // Step 1: Transcribe (already happening)
    try await recorder.stopRecordingAndTranscribe()

    // Step 2: Protect PII on-device
    let protected = await PIIProtectionManager.shared.protectTranscript(
        recorder.transcriptionText
    )

    // Step 3: Show agent reasoning (optional, for demo/debug)
    for step in protected.reasoning {
        print(step)
    }

    // Step 4: Save recording with protected transcript
    let recording = Recording(
        transcript: protected.redacted,      // Safe for upload
        originalTranscript: protected.original,  // Keep encrypted locally
        protectionApplied: protected.wasRedacted,
        piiStats: protected.stats
    )

    // Step 5: Upload only redacted version
    await uploadToBackend(recording)
}
```

## Example Output

### Input Transcript:
```
"Hi, I'm John Smith and I work at Tesla. You can reach me at
john.smith@tesla.com or call me at (555) 123-4567. I live at
123 Main Street in Palo Alto, California 94301. Let's grab
coffee next week!"
```

### Agent Reasoning:
```
🛡️ Starting PII scan...
✓ Found 1 Email
✓ Found 1 Phone Number
✓ Found 1 Street Address
✓ Found 1 City
✓ Found 1 State/Province
✓ Found 1 ZIP Code
→ Redacting Email: 'john.smith@tesla.com' → '[EMAIL_1]'
→ Redacting Phone Number: '(555) 123-4567' → '[PHONE_1]'
→ Redacting Street Address: '123 Main Street' → '[STREET_ADDRESS_1]'
→ Redacting City: 'Palo Alto' → '[CITY_1]'
→ Redacting State/Province: 'California' → '[STATE_1]'
→ Redacting ZIP Code: '94301' → '[ZIP_1]'
✅ Protection complete! 6 PII entities redacted
```

### Output (Redacted):
```
"Hi, I'm John Smith and I work at Tesla. You can reach me at
[EMAIL_1] or call me at [PHONE_1]. I live at [STREET_ADDRESS_1]
in [CITY_1], [STATE_1] [ZIP_1]. Let's grab coffee next week!"
```

**Note:** Names (John Smith) and company (Tesla) are preserved for networking context!

## Files

- `Agent.swift` - Base agent protocol and data structures
- `PIIDetectionTools.swift` - Individual PII detectors
- `PIIGuardianAgent.swift` - Main agent orchestrator
- `PIIGuardianIntegration.swift` - Integration helpers and examples

## Privacy Guarantees

1. ✅ **100% On-Device** - No API calls, no data leaves device during redaction
2. ✅ **Runs Before Upload** - PII removed before any network transmission
3. ✅ **Transparent** - Shows what was redacted and why
4. ✅ **Reversible** - Original stored encrypted locally (optional)
5. ✅ **Fast** - Regex + pattern matching, no ML inference needed

## Future Enhancements

- [ ] Add support for international addresses
- [ ] Detect dates of birth
- [ ] Detect medical information
- [ ] User-configurable redaction rules
- [ ] Option to use on-device LLM for contextual detection
- [ ] Integration with Apple's Data Detection APIs

## Testing

See `PIIGuardianTests.swift` for comprehensive test cases covering all detection scenarios.
