#!/usr/bin/env python3
"""Test the complete upload flow"""
import requests
import json

BASE_URL = "http://10.32.82.43:8000"

print("=== Testing Complete Upload Flow ===\n")

# Test 1: Backend is reachable
print("1. Testing if backend is reachable...")
try:
    response = requests.get(f"{BASE_URL}/docs", timeout=5)
    if response.status_code == 200:
        print("   ✅ Backend is reachable")
    else:
        print(f"   ❌ Backend returned {response.status_code}")
        exit(1)
except Exception as e:
    print(f"   ❌ Cannot reach backend: {e}")
    print(f"   Make sure backend is running: uvicorn main:app --reload --host 0.0.0.0 --port 8000")
    exit(1)

# Test 2: Test append-transcript endpoint
print("\n2. Testing /append-transcript endpoint...")
try:
    data = {
        'transcript_text': 'Test transcript from Python flow test',
        'event_name': 'test_flow_event',
        'location': 'Test Location'
    }

    response = requests.post(
        f"{BASE_URL}/audio/append-transcript",
        data=data,
        timeout=30
    )

    if response.status_code == 200:
        result = response.json()
        print(f"   ✅ Upload successful!")
        print(f"   📄 File: {result['transcript_file_path']}")
        print(f"   📊 Chars: {result['character_count']}")
    else:
        print(f"   ❌ Upload failed: {response.status_code}")
        print(f"   Response: {response.text}")
        exit(1)
except Exception as e:
    print(f"   ❌ Request failed: {e}")
    exit(1)

# Test 3: Verify in GCS
print("\n3. Verifying file in GCS bucket...")
try:
    from google.cloud import storage
    from google.oauth2 import service_account

    creds = service_account.Credentials.from_service_account_file('./aperta-service-account.json')
    client = storage.Client(credentials=creds, project='aperta-487501')

    blob = client.bucket('aperta').blob('transcripts/test_flow_event.txt')
    if blob.exists():
        content = blob.download_as_text()
        print(f"   ✅ File exists in GCS!")
        print(f"   📝 Content: {content[-100:]}")
    else:
        print(f"   ❌ File NOT found in GCS")
        exit(1)

except Exception as e:
    print(f"   ❌ GCS check failed: {e}")
    exit(1)

print("\n✅ ALL TESTS PASSED!")
print("\nIf this works but mobile doesn't, the issue is in the mobile app.")
