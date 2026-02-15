#!/usr/bin/env python3
"""Test script to verify GCS upload works"""

import asyncio
import sys
sys.path.insert(0, '.')

from services.storage import StorageService, StorageConfig
from config import settings

async def main():
    print("=== Testing GCS Upload ===\n")

    # Check settings
    print(f"GCP Project ID: {settings.gcp_project_id}")
    print(f"GCP Bucket: {settings.gcp_bucket_name}")
    print(f"Service Account: {settings.gcp_service_account_json}")
    print()

    # Initialize storage
    print("Initializing StorageService...")
    config = StorageConfig(
        local_storage_path="./uploads",
        use_gcp=True,
        gcp_bucket=settings.gcp_bucket_name,
        gcp_project_id=settings.gcp_project_id,
        gcp_service_account_json=settings.gcp_service_account_json,
    )
    storage = StorageService(config)
    print(f"Storage info: {storage.get_storage_info()}")
    print()

    # Test append
    test_text = "This is a test transcript from Python script"
    event_name = "test_event_python"

    print(f"Appending to event: {event_name}")
    result = await storage.append_transcript(
        transcript_text=test_text,
        event_name=event_name
    )
    print(f"Result: {result}")
    print()

    print("✅ Test complete!")
    print(f"Check: gs://aperta/transcripts/{event_name}.txt")

if __name__ == "__main__":
    asyncio.run(main())
