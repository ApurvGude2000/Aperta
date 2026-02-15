# ABOUTME: Google Cloud Storage utility for managing all GCS bucket operations.
# ABOUTME: Handles audio files, transcripts with append capability, and ChromaDB persistence.

from google.cloud import storage
from google.oauth2 import service_account
import os
import shutil
from pathlib import Path
from typing import Optional
from config import settings
from utils.logger import setup_logger

logger = setup_logger(__name__)


class GCSStorage:
    """Google Cloud Storage handler for ChromaDB persistence."""

    def __init__(self):
        """Initialize GCS client with service account credentials."""
        self.bucket_name = settings.gcp_bucket_name
        self.client = None
        self.bucket = None

        try:
            if settings.gcp_service_account_json:
                credentials = service_account.Credentials.from_service_account_file(
                    settings.gcp_service_account_json
                )
                self.client = storage.Client(
                    credentials=credentials,
                    project=settings.gcp_project_id
                )
            else:
                # For Cloud Run, use default credentials
                self.client = storage.Client(project=settings.gcp_project_id)

            self.bucket = self.client.bucket(self.bucket_name)
            logger.info(f"GCS client initialized for bucket: {self.bucket_name}")
        except Exception as e:
            logger.error(f"Failed to initialize GCS client: {e}")
            raise

    def upload_directory(self, local_dir: str, gcs_prefix: str = "chroma_db/") -> bool:
        """
        Upload entire directory to GCS bucket.

        Args:
            local_dir: Local directory path
            gcs_prefix: GCS prefix (folder) to upload to

        Returns:
            bool: Success status
        """
        try:
            local_path = Path(local_dir)
            if not local_path.exists():
                logger.warning(f"Local directory does not exist: {local_dir}")
                return False

            file_count = 0
            for file_path in local_path.rglob("*"):
                if file_path.is_file():
                    # Calculate relative path
                    relative_path = file_path.relative_to(local_path)
                    gcs_path = f"{gcs_prefix}{relative_path}"

                    # Upload file
                    blob = self.bucket.blob(gcs_path)
                    blob.upload_from_filename(str(file_path))
                    file_count += 1

            logger.info(f"Uploaded {file_count} files from {local_dir} to gs://{self.bucket_name}/{gcs_prefix}")
            return True

        except Exception as e:
            logger.error(f"Failed to upload directory: {e}")
            return False

    def download_directory(self, gcs_prefix: str, local_dir: str) -> bool:
        """
        Download entire directory from GCS bucket.

        Args:
            gcs_prefix: GCS prefix (folder) to download from
            local_dir: Local directory to download to

        Returns:
            bool: Success status
        """
        try:
            # Create local directory
            local_path = Path(local_dir)
            local_path.mkdir(parents=True, exist_ok=True)

            # List all blobs with prefix
            blobs = self.bucket.list_blobs(prefix=gcs_prefix)

            file_count = 0
            for blob in blobs:
                # Skip directory markers
                if blob.name.endswith('/'):
                    continue

                # Calculate local path
                relative_path = blob.name[len(gcs_prefix):]
                local_file_path = local_path / relative_path

                # Create parent directories
                local_file_path.parent.mkdir(parents=True, exist_ok=True)

                # Download file
                blob.download_to_filename(str(local_file_path))
                file_count += 1

            logger.info(f"Downloaded {file_count} files from gs://{self.bucket_name}/{gcs_prefix} to {local_dir}")
            return True

        except Exception as e:
            logger.error(f"Failed to download directory: {e}")
            return False

    def sync_to_gcs(self, local_dir: str, gcs_prefix: str = "chroma_db/") -> bool:
        """
        Sync local ChromaDB directory to GCS (backup).

        Args:
            local_dir: Local ChromaDB persist directory
            gcs_prefix: GCS prefix for ChromaDB data

        Returns:
            bool: Success status
        """
        logger.info(f"Syncing ChromaDB data to GCS: {local_dir} -> gs://{self.bucket_name}/{gcs_prefix}")
        return self.upload_directory(local_dir, gcs_prefix)

    def sync_from_gcs(self, gcs_prefix: str, local_dir: str) -> bool:
        """
        Sync ChromaDB directory from GCS to local (restore).

        Args:
            gcs_prefix: GCS prefix for ChromaDB data
            local_dir: Local ChromaDB persist directory

        Returns:
            bool: Success status
        """
        logger.info(f"Syncing ChromaDB data from GCS: gs://{self.bucket_name}/{gcs_prefix} -> {local_dir}")
        return self.download_directory(gcs_prefix, local_dir)

    def backup_database_file(self, db_file_path: str, gcs_path: str = "backups/aperta.db") -> bool:
        """
        Upload database file to GCS (for backup purposes only).

        Args:
            db_file_path: Local database file path
            gcs_path: GCS destination path

        Returns:
            bool: Success status
        """
        try:
            if not os.path.exists(db_file_path):
                logger.warning(f"Database file does not exist: {db_file_path}")
                return False

            blob = self.bucket.blob(gcs_path)
            blob.upload_from_filename(db_file_path)
            logger.info(f"Backed up database to gs://{self.bucket_name}/{gcs_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to backup database: {e}")
            return False

    def save_audio_file(
        self,
        file_data: bytes,
        event_name: str,
        filename: str,
        content_type: str = "audio/m4a"
    ) -> Optional[str]:
        """
        Save audio file to GCS bucket.

        Args:
            file_data: Audio file bytes
            event_name: Event name for organizing files
            filename: Filename with extension (e.g., "20240215_143000.m4a")
            content_type: MIME type of the audio file

        Returns:
            GCS path if successful, None otherwise
        """
        try:
            gcs_path = f"audio/{event_name}/{filename}"
            blob = self.bucket.blob(gcs_path)
            blob.upload_from_string(file_data, content_type=content_type)
            logger.info(f"Saved audio file to gs://{self.bucket_name}/{gcs_path}")
            return gcs_path

        except Exception as e:
            logger.error(f"Failed to save audio file: {e}")
            return None

    def get_transcript(self, event_name: str) -> Optional[str]:
        """
        Get transcript content for an event.

        Args:
            event_name: Event name

        Returns:
            Transcript text if exists, empty string if not found, None on error
        """
        try:
            gcs_path = f"transcripts/{event_name}.txt"
            blob = self.bucket.blob(gcs_path)

            if not blob.exists():
                logger.info(f"Transcript does not exist yet: {gcs_path}")
                return ""

            content = blob.download_as_text()
            logger.info(f"Downloaded transcript from gs://{self.bucket_name}/{gcs_path} ({len(content)} chars)")
            return content

        except Exception as e:
            logger.error(f"Failed to get transcript: {e}")
            return None

    def append_to_transcript(self, event_name: str, new_transcript: str) -> bool:
        """
        Append new transcript to existing event transcript file.
        If file doesn't exist, creates it.

        Args:
            event_name: Event name
            new_transcript: New transcript text to append

        Returns:
            bool: Success status
        """
        try:
            gcs_path = f"transcripts/{event_name}.txt"

            # Get existing content
            existing_content = self.get_transcript(event_name)
            if existing_content is None:
                logger.error(f"Failed to get existing transcript for {event_name}")
                return False

            # Append new content with separator
            separator = "\n\n---\n\n" if existing_content else ""
            updated_content = existing_content + separator + new_transcript

            # Upload updated content
            blob = self.bucket.blob(gcs_path)
            blob.upload_from_string(updated_content, content_type="text/plain")

            logger.info(f"Appended {len(new_transcript)} chars to gs://{self.bucket_name}/{gcs_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to append to transcript: {e}")
            return False

    def save_transcript(self, event_name: str, transcript_content: str) -> Optional[str]:
        """
        Save/overwrite transcript file for an event.

        Args:
            event_name: Event name
            transcript_content: Full transcript text

        Returns:
            GCS path if successful, None otherwise
        """
        try:
            gcs_path = f"transcripts/{event_name}.txt"
            blob = self.bucket.blob(gcs_path)
            blob.upload_from_string(transcript_content, content_type="text/plain")
            logger.info(f"Saved transcript to gs://{self.bucket_name}/{gcs_path} ({len(transcript_content)} chars)")
            return gcs_path

        except Exception as e:
            logger.error(f"Failed to save transcript: {e}")
            return None


def get_gcs_storage() -> Optional[GCSStorage]:
    """
    Get GCS storage instance if configured.

    Returns:
        GCSStorage instance or None
    """
    if settings.use_gcs_for_chroma and settings.gcp_bucket_name:
        try:
            return GCSStorage()
        except Exception as e:
            logger.error(f"Failed to create GCS storage: {e}")
            return None
    return None
