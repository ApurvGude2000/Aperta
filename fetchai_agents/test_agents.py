#!/usr/bin/env python3
# ABOUTME: Test script to verify Fetch.ai agents are working correctly.
# ABOUTME: Sends sample requests to each agent and validates responses.

import asyncio
import httpx
from datetime import datetime


async def test_backend_connection():
    """Test that backend is accessible."""
    print("🔍 Testing backend connection...")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:8000/health")
            if response.status_code == 200:
                print("✓ Backend is running")
                return True
            else:
                print(f"❌ Backend returned status {response.status_code}")
                return False
    except Exception as e:
        print(f"❌ Cannot connect to backend: {e}")
        print("   Make sure backend is running: cd ../backend && python main.py")
        return False


async def test_privacy_agent():
    """Test privacy redaction via direct HTTP."""
    print("\n🔍 Testing Privacy Guardian Agent...")
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            # Direct call to privacy agent (if running)
            response = await client.post(
                "http://localhost:8003/submit",
                json={
                    "transcript": "Call me at 555-1234 or email john@example.com",
                    "redact_emails": True,
                    "redact_phones": True,
                    "redact_addresses": False,
                    "redact_names": False,
                },
            )
            if response.status_code == 200:
                data = response.json()
                print(f"✓ Privacy agent responding")
                print(f"  Redacted: {data.get('redacted_text', 'N/A')}")
                return True
            else:
                print(f"❌ Privacy agent returned status {response.status_code}")
                return False
    except httpx.ConnectError:
        print("⚠️  Privacy agent not running (expected if bureau not started)")
        return None
    except Exception as e:
        print(f"❌ Privacy agent error: {e}")
        return False


async def test_qa_router():
    """Test Q&A router via direct HTTP."""
    print("\n🔍 Testing Q&A Router Agent...")
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                "http://localhost:8006/submit",
                json={
                    "question": "What topics have been discussed?",
                    "use_rag": True,
                    "max_context_conversations": 5,
                },
            )
            if response.status_code == 200:
                data = response.json()
                print(f"✓ Q&A router responding")
                print(f"  Agents used: {data.get('agents_used', [])}")
                return True
            else:
                print(f"❌ Q&A router returned status {response.status_code}")
                return False
    except httpx.ConnectError:
        print("⚠️  Q&A router not running (expected if bureau not started)")
        return None
    except Exception as e:
        print(f"❌ Q&A router error: {e}")
        return False


async def main():
    """Run all tests."""
    print("=" * 60)
    print("Fetch.ai Agent Test Suite")
    print("=" * 60)
    print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # Test backend first
    backend_ok = await test_backend_connection()
    if not backend_ok:
        print("\n❌ Backend is not running. Cannot proceed with agent tests.")
        print("   Start backend first: cd ../backend && python main.py")
        return

    # Test agents
    privacy_result = await test_privacy_agent()
    qa_result = await test_qa_router()

    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    print(f"Backend:       {'✓ Running' if backend_ok else '❌ Failed'}")
    print(f"Privacy Agent: {'✓ Working' if privacy_result else ('⚠️  Not started' if privacy_result is None else '❌ Failed')}")
    print(f"Q&A Router:    {'✓ Working' if qa_result else ('⚠️  Not started' if qa_result is None else '❌ Failed')}")
    print()

    if privacy_result is None or qa_result is None:
        print("💡 Agents are not running. Start with: python main.py")
    elif privacy_result and qa_result:
        print("✅ All tests passed!")
    else:
        print("❌ Some tests failed. Check logs for details.")

    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
