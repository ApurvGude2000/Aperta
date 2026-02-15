// ABOUTME: Test examples for PII Guardian Agent
// ABOUTME: Demonstrates detection and redaction capabilities

import Foundation

/// Test examples showing PII Guardian in action
class PIIGuardianTestExamples {

    static func runAllTests() async {
        print("=" * 60)
        print("PII GUARDIAN AGENT - TEST EXAMPLES")
        print("=" * 60)
        print()

        await testNetworkingConversation()
        await testComplexScenario()
        await testCleanTranscript()
        await testEdgeCases()
    }

    // MARK: - Test 1: Typical Networking Conversation

    static func testNetworkingConversation() async {
        print("📝 TEST 1: Typical Networking Conversation")
        print("-" * 60)

        let transcript = """
        Hi, I'm Sarah Johnson and I work at Google as a Product Manager.
        You can reach me at sarah.johnson@google.com or call me at
        (650) 555-1234. I'm based in Mountain View, California. Let's
        definitely stay in touch!
        """

        let guardian = PIIGuardianAgent()
        let result = await guardian.execute(input: transcript)

        printResult(input: transcript, result: result)
    }

    // MARK: - Test 2: Complex Multi-PII Scenario

    static func testComplexScenario() async {
        print("\n📝 TEST 2: Complex Multi-PII Scenario")
        print("-" * 60)

        let transcript = """
        Great meeting you at the conference! I'm Michael Chen from
        Tesla. Feel free to email me at mchen@tesla.com or my personal
        email michael.chen.123@gmail.com. My work number is 650-555-9876
        and cell is (415) 555-4321. Our office is at 3500 Deer Creek Road
        in Palo Alto, CA 94304. I'm also traveling to Austin next month -
        staying near 1234 Congress Avenue, Austin, TX 78701. Looking
        forward to collaborating with you at Microsoft!
        """

        let guardian = PIIGuardianAgent()
        let result = await guardian.execute(input: transcript)

        printResult(input: transcript, result: result)
    }

    // MARK: - Test 3: Clean Transcript (No PII)

    static func testCleanTranscript() async {
        print("\n📝 TEST 3: Clean Transcript (No PII)")
        print("-" * 60)

        let transcript = """
        I really enjoyed discussing the future of AI at the conference.
        The presentation about machine learning was fascinating. I think
        there's huge potential in this space. Would love to hear your
        thoughts on the topic!
        """

        let guardian = PIIGuardianAgent()
        let result = await guardian.execute(input: transcript)

        printResult(input: transcript, result: result)
    }

    // MARK: - Test 4: Edge Cases

    static func testEdgeCases() async {
        print("\n📝 TEST 4: Edge Cases")
        print("-" * 60)

        let transcript = """
        Let me give you my number: 5-5-5, 1-2-3-4. Or you can try
        my other line at 555.123.4567. My ZIP is 12345 but I'm
        moving to 94102-1234 next month. Email me at test+tag@example.co.uk
        """

        let guardian = PIIGuardianAgent()
        let result = await guardian.execute(input: transcript)

        printResult(input: transcript, result: result)
    }

    // MARK: - Helper Methods

    static func printResult(input: String, result: AgentResult) {
        print("\n📄 ORIGINAL:")
        print(input)

        print("\n🛡️ AGENT REASONING:")
        for step in result.reasoning {
            print("  " + step)
        }

        print("\n🔒 REDACTED OUTPUT:")
        print(result.output)

        if let stats = result.metadata["types_summary"] as? [String] {
            print("\n📊 STATISTICS:")
            for stat in stats {
                print("  • " + stat)
            }
        }

        print("\n" + "=" * 60)
    }
}

// MARK: - Quick Test Runner

extension String {
    static func *(lhs: String, rhs: Int) -> String {
        return String(repeating: lhs, count: rhs)
    }
}

// MARK: - Usage in App

/*

 // In your app, you can run tests like this:

 Task {
     await PIIGuardianTestExamples.runAllTests()
 }

 // Or test with your own transcript:

 let guardian = PIIGuardianAgent()
 let result = await guardian.execute(input: "Your transcript here...")

 print("Protected transcript:")
 print(result.output)

 */
