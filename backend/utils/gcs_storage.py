# ABOUTME: Google Cloud Storage utility for managing ChromaDB persistence in GCS buckets.
# ABOUTME: Handles upload/download of ChromaDB data and provides GCS bucket operations.

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

        if settings.gcp_service_account_json:
            try:
                credentials = service_account.Credentials.from_service_account_file(
                    settings.gcp_service_account_json
                )
                self.client = storage.Client(
                    credentials=credentials,
                    project=settings.gcp_project_id
                )
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
