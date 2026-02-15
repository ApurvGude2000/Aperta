"""
Script to update the local aperta.db with all transcript files from GCS transcripts/ folder,
then upload the updated DB to gs://aperta/backups/aperta.db.
"""
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import sqlite3
import uuid
from datetime import datetime
from services.transcript_storage import transcript_storage
from utils.gcs_storage import GCSStorage


def main():
    db_path = os.path.join(os.path.dirname(__file__), "..", "aperta.db")
    db_path = os.path.abspath(db_path)
    print(f"Database path: {db_path}")

    # 1. Fetch all transcripts from GCS
    print("\n=== Fetching transcripts from GCS ===")
    transcripts_meta = transcript_storage.list_transcripts()
    print(f"Found {len(transcripts_meta)} transcript files in GCS")

    # 2. Connect to local SQLite DB
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Ensure conversations table exists
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS conversations (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            title TEXT,
            status TEXT DEFAULT 'completed',
            transcript TEXT,
            recording_url TEXT,
            location TEXT,
            event_name TEXT,
            started_at DATETIME,
            ended_at DATETIME,
            created_at DATETIME,
            updated_at DATETIME
        )
    """)

    # 3. Get existing conversation titles to avoid duplicates
    cursor.execute("SELECT title, id FROM conversations")
    existing = {row[0]: row[1] for row in cursor.fetchall()}
    print(f"Existing conversations in DB: {len(existing)}")

    # 4. Insert/update each transcript
    inserted = 0
    updated = 0
    skipped = 0

    for meta in transcripts_meta:
        transcript_id = meta.get("id", "")
        title = meta.get("title", transcript_id)
        size = meta.get("size", 0)
        created_at = meta.get("created_at", "")

        # Skip tiny files
        if size < 50:
            print(f"  SKIP (too small): {title} ({size} bytes)")
            skipped += 1
            continue

        # Fetch content
        content = transcript_storage.get_transcript_content(transcript_id)
        if not content:
            print(f"  SKIP (no content): {title}")
            skipped += 1
            continue

        now = datetime.utcnow().isoformat()

        if title in existing:
            # Update existing record
            cursor.execute("""
                UPDATE conversations
                SET transcript = ?, updated_at = ?, status = 'completed'
                WHERE id = ?
            """, (content, now, existing[title]))
            print(f"  UPDATED: {title} ({len(content)} chars)")
            updated += 1
        else:
            # Insert new record
            conv_id = str(uuid.uuid4())
            cursor.execute("""
                INSERT INTO conversations (id, user_id, title, status, transcript, event_name, started_at, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (conv_id, "default_user", title, "completed", content, title, created_at or now, created_at or now, now))
            print(f"  INSERTED: {title} ({len(content)} chars)")
            inserted += 1

    conn.commit()

    # 5. Verify
    cursor.execute("SELECT COUNT(*) FROM conversations")
    total = cursor.fetchone()[0]
    cursor.execute("SELECT title, LENGTH(transcript) FROM conversations ORDER BY created_at DESC")
    rows = cursor.fetchall()

    print(f"\n=== Summary ===")
    print(f"Inserted: {inserted}, Updated: {updated}, Skipped: {skipped}")
    print(f"Total conversations in DB: {total}")
    for title, length in rows:
        print(f"  - {title}: {length or 0} chars")

    conn.close()

    # 6. Upload updated DB to GCS
    print(f"\n=== Uploading updated DB to GCS ===")
    try:
        gcs = GCSStorage()
        success = gcs.backup_database_file(db_path, "backups/aperta.db")
        if success:
            print(f"Successfully uploaded {db_path} to gs://aperta/backups/aperta.db")
        else:
            print("Failed to upload DB to GCS")
    except Exception as e:
        print(f"Error uploading to GCS: {e}")


if __name__ == "__main__":
    main()
