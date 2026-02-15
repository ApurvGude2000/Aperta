#!/usr/bin/env python3
# ABOUTME: Migration script to move from local SQLite + local files to GCP (Cloud SQL + GCS).
# ABOUTME: Exports SQLite data, uploads to Cloud SQL, and syncs ChromaDB to GCS bucket.

"""
GCP Migration Script

This script migrates your Aperta backend from local storage to GCP:
1. Exports data from SQLite
2. Uploads to Cloud SQL PostgreSQL
3. Syncs ChromaDB embeddings to GCS bucket
4. Backs up SQLite file to GCS (for safety)

Usage:
    python scripts/migrate_to_gcp.py
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import create_async_engine
import pandas as pd
from utils.gcs_storage import GCSStorage
from utils.cloud_sql import get_cloud_sql_engine, should_use_cloud_sql
from config import settings
from utils.logger import setup_logger

logger = setup_logger(__name__)


async def export_sqlite_data():
    """Export all data from SQLite database."""
    logger.info("Exporting data from SQLite...")

    # Connect to SQLite
    sqlite_url = settings.database_url
    engine = create_engine(sqlite_url.replace("sqlite+aiosqlite://", "sqlite://"))

    tables = [
        "conversations",
        "participants",
        "entities",
        "action_items",
        "privacy_audit_logs",
        "follow_up_messages",
        "user_goals",
        "opportunities",
        "qa_sessions",
        "qa_interactions"
    ]

    exported_data = {}

    with engine.connect() as conn:
        for table in tables:
            try:
                # Check if table exists
                result = conn.execute(text(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'"))
                if not result.fetchone():
                    logger.warning(f"Table {table} does not exist, skipping")
                    continue

                # Export table data
                df = pd.read_sql_table(table, conn)
                exported_data[table] = df
                logger.info(f"Exported {len(df)} rows from {table}")
            except Exception as e:
                logger.error(f"Error exporting {table}: {e}")

    return exported_data


async def import_to_cloud_sql(exported_data: dict):
    """Import data to Cloud SQL PostgreSQL."""
    logger.info("Importing data to Cloud SQL...")

    # Get Cloud SQL engine
    engine = await get_cloud_sql_engine()

    async with engine.begin() as conn:
        for table_name, df in exported_data.items():
            try:
                # Import data (pandas to_sql doesn't support async, so we'll insert manually)
                logger.info(f"Importing {len(df)} rows to {table_name}...")

                # Convert DataFrame to list of dicts
                records = df.to_dict('records')

                if records:
                    # Build insert statement
                    columns = list(records[0].keys())
                    placeholders = ", ".join([f":{col}" for col in columns])
                    insert_sql = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({placeholders})"

                    # Execute batch insert
                    await conn.execute(text(insert_sql), records)
                    logger.info(f"✓ Imported {len(records)} rows to {table_name}")

            except Exception as e:
                logger.error(f"Error importing to {table_name}: {e}")

    await engine.dispose()
    logger.info("Data import complete")


async def sync_chroma_to_gcs():
    """Sync ChromaDB data to GCS bucket."""
    logger.info("Syncing ChromaDB to GCS...")

    try:
        gcs = GCSStorage()
        local_chroma_dir = settings.chroma_persist_dir

        if Path(local_chroma_dir).exists():
            success = gcs.sync_to_gcs(local_chroma_dir, "chroma_db/")
            if success:
                logger.info("✓ ChromaDB synced to GCS successfully")
            else:
                logger.error("✗ Failed to sync ChromaDB to GCS")
        else:
            logger.warning(f"ChromaDB directory not found: {local_chroma_dir}")

    except Exception as e:
        logger.error(f"Error syncing ChromaDB to GCS: {e}")


async def backup_sqlite_to_gcs():
    """Backup SQLite file to GCS (for safety)."""
    logger.info("Backing up SQLite database to GCS...")

    try:
        gcs = GCSStorage()
        db_file = "aperta.db"  # or "networkai.db" depending on your setup

        if Path(db_file).exists():
            success = gcs.backup_database_file(db_file, f"backups/{db_file}")
            if success:
                logger.info("✓ SQLite backup uploaded to GCS")
            else:
                logger.error("✗ Failed to backup SQLite to GCS")
        else:
            logger.warning(f"SQLite database file not found: {db_file}")

    except Exception as e:
        logger.error(f"Error backing up SQLite: {e}")


async def main():
    """Main migration workflow."""
    print("=" * 80)
    print("APERTA GCP MIGRATION")
    print("=" * 80)
    print()

    # Check configuration
    if not should_use_cloud_sql():
        print("❌ Cloud SQL not configured!")
        print("Please set these environment variables:")
        print("  - CLOUD_SQL_INSTANCE_CONNECTION_NAME")
        print("  - CLOUD_SQL_PASSWORD")
        return

    if not settings.gcp_bucket_name:
        print("❌ GCS bucket not configured!")
        print("Please set: GCP_BUCKET_NAME")
        return

    print("Configuration:")
    print(f"  Cloud SQL Instance: {settings.cloud_sql_instance_connection_name}")
    print(f"  GCS Bucket: {settings.gcp_bucket_name}")
    print()

    # Confirm migration
    response = input("Proceed with migration? (yes/no): ")
    if response.lower() != "yes":
        print("Migration cancelled")
        return

    print()
    print("Starting migration...")
    print()

    try:
        # Step 1: Export SQLite data
        print("Step 1/4: Exporting SQLite data...")
        exported_data = await export_sqlite_data()
        print(f"✓ Exported {len(exported_data)} tables")
        print()

        # Step 2: Import to Cloud SQL
        print("Step 2/4: Importing to Cloud SQL...")
        await import_to_cloud_sql(exported_data)
        print()

        # Step 3: Sync ChromaDB to GCS
        print("Step 3/4: Syncing ChromaDB to GCS...")
        await sync_chroma_to_gcs()
        print()

        # Step 4: Backup SQLite to GCS
        print("Step 4/4: Backing up SQLite to GCS...")
        await backup_sqlite_to_gcs()
        print()

        print("=" * 80)
        print("✅ MIGRATION COMPLETE!")
        print("=" * 80)
        print()
        print("Next steps:")
        print("1. Update your .env file to use Cloud SQL (see instructions)")
        print("2. Restart your backend server")
        print("3. Test that everything works")
        print("4. Once confirmed, you can delete local aperta.db and chroma_db/")

    except Exception as e:
        logger.error(f"Migration failed: {e}", exc_info=True)
        print()
        print("❌ Migration failed! Check logs for details.")


if __name__ == "__main__":
    asyncio.run(main())
