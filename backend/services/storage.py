"""
Storage service for managing audio files and transcriptions.
Supports both local filesystem and GCP cloud storage.
"""

import os
from pathlib import Path
from typing import Optional, Dict, Any
import logging
from datetime import datetime
import aiofiles
import aiofiles.os
from utils.gcs_storage import GCSStorage

logger = logging.getLogger(__name__)


class StorageConfig:
    """Storage configuration."""

    def __init__(
        self,
        local_storage_path: str = "./uploads",
        use_gcp: bool = False,
        gcp_bucket: Optional[str] = None,
        gcp_project_id: Optional[str] = None,
        gcp_service_account_json: Optional[str] = None,
    ):
        self.local_storage_path = local_storage_path
        self.use_gcp = use_gcp
        self.gcp_bucket = gcp_bucket
        self.gcp_project_id = gcp_project_id
        self.gcp_service_account_json = gcp_service_account_json

        # Create local storage directory if it doesn't exist
        Path(self.local_storage_path).mkdir(parents=True, exist_ok=True)


class StorageService:
    """
    Unified storage service for audio files and transcriptions.

    Supports:
    - Local filesystem storage (development)
    - GCP cloud storage (production)
    - Automatic path organization
    - Transcript appending
    """

    def __init__(self, config):
        """
        Initialize storage service.

        Args:
            config: StorageConfig instance or Settings object with storage configuration
        """
        # Convert Settings object to StorageConfig if needed
        if not isinstance(config, StorageConfig):
            # Assume it's a Settings object
            self.config = StorageConfig(
                local_storage_path=getattr(config, 'local_storage_path', './uploads'),
                use_gcp=getattr(config, 'gcp_bucket_name', None) is not None,
                gcp_bucket=getattr(config, 'gcp_bucket_name', None),
                gcp_project_id=getattr(config, 'gcp_project_id', None),
                gcp_service_account_json=getattr(config, 'gcp_service_account_json', None),
            )
        else:
            self.config = config

        self.gcs_storage = None

        if self.config.use_gcp:
            self._init_gcp()

        logger.info(
            f"StorageService initialized: "
            f"local={self.config.local_storage_path}, "
            f"gcp={'enabled' if self.config.use_gcp else 'disabled'}"
        )

    def _init_gcp(self):
        """Initialize GCP client."""
        try:
            self.gcs_storage = GCSStorage()
            logger.info(f"GCS client initialized: bucket={self.config.gcp_bucket}")
        except Exception as e:
            logger.warning(f"Failed to initialize GCS client: {e}. Using local storage only.")
            self.config.use_gcp = False

    async def save_audio_file(
        self,
        file_content: bytes,
        event_name: str,
        filename: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Save audio file to storage.

        Args:
            file_content: Raw audio file bytes
            event_name: Event name for organizing files
            filename: Original filename with extension
            metadata: Optional metadata

        Returns:
            Path/URL where file was saved
        """
        try:
            if self.config.use_gcp and self.gcs_storage:
                return await self._save_to_gcp(file_content, event_name, filename, metadata)
            else:
                return await self._save_to_local(file_content, event_name, filename, metadata)

        except Exception as e:
            logger.error(f"Error saving audio file: {e}")
            raise

    async def _save_to_local(
        self,
        file_content: bytes,
        event_name: str,
        filename: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Save file to local filesystem."""
        try:
            # Create directory structure: audio/{event_name}/{filename}
            file_path = f"audio/{event_name}/{filename}"
            full_path = Path(self.config.local_storage_path) / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)

            # Write file
            async with aiofiles.open(full_path, "wb") as f:
                await f.write(file_content)

            logger.info(f"Audio file saved locally: {full_path}")

            # Save metadata if provided
            if metadata:
                await self._save_metadata(full_path, metadata)

            # Return relative path for storage
            return str(full_path)

        except Exception as e:
            logger.error(f"Error saving to local storage: {e}")
            raise

    async def _save_to_gcp(
        self,
        file_content: bytes,
        event_name: str,
        filename: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Save file to GCP bucket."""
        try:
            # Determine content type from filename
            content_type = "audio/m4a"
            if filename.lower().endswith('.mp3'):
                content_type = "audio/mpeg"
            elif filename.lower().endswith('.wav'):
                content_type = "audio/wav"

            # Upload to GCS
            gcs_path = self.gcs_storage.save_audio_file(
                file_data=file_content,
                event_name=event_name,
                filename=filename,
                content_type=content_type
            )

            if gcs_path:
                logger.info(f"Audio file saved to GCS: gs://{self.config.gcp_bucket}/{gcs_path}")
                return f"gs://{self.config.gcp_bucket}/{gcs_path}"
            else:
                raise Exception("Failed to save audio file to GCS")

        except Exception as e:
            logger.error(f"Error saving to GCP: {e}")
            raise

    async def append_transcript(
        self,
        transcript_text: str,
        event_name: str,
    ) -> str:
        """
        Append transcript text to event's transcript file.
        Creates file if it doesn't exist.

        Args:
            transcript_text: Formatted transcript text to append
            event_name: Event name (determines filename: transcripts/{event_name}.txt)

        Returns:
            Path/URL where transcript was saved
        """
        try:
            if self.config.use_gcp and self.gcs_storage:
                return await self._append_transcript_to_gcp(transcript_text, event_name)
            else:
                return await self._append_transcript_local(transcript_text, event_name)

        except Exception as e:
            logger.error(f"Error appending transcript: {e}")
            raise

    async def _append_transcript_local(self, transcript_text: str, event_name: str) -> str:
        """Append transcript to local file."""
        try:
            # File path: transcripts/{event_name}.txt
            file_path = f"transcripts/{event_name}.txt"
            full_path = Path(self.config.local_storage_path) / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)

            # Read existing content if file exists
            existing_content = ""
            if full_path.exists():
                async with aiofiles.open(full_path, "r", encoding="utf-8") as f:
                    existing_content = await f.read()

            # Append with separator
            separator = "\n\n---\n\n" if existing_content else ""
            updated_content = existing_content + separator + transcript_text

            # Write updated content
            async with aiofiles.open(full_path, "w", encoding="utf-8") as f:
                await f.write(updated_content)

            logger.info(f"Appended {len(transcript_text)} chars to local transcript: {full_path}")
            return str(full_path)

        except Exception as e:
            logger.error(f"Error appending transcript locally: {e}")
            raise

    async def _append_transcript_to_gcp(self, transcript_text: str, event_name: str) -> str:
        """Append transcript to GCP bucket file."""
        try:
            # Use GCSStorage append method
            success = self.gcs_storage.append_to_transcript(event_name, transcript_text)

            if success:
                gcs_path = f"transcripts/{event_name}.txt"
                logger.info(f"Appended transcript to GCS: gs://{self.config.gcp_bucket}/{gcs_path}")
                return f"gs://{self.config.gcp_bucket}/{gcs_path}"
            else:
                raise Exception("Failed to append transcript to GCS")

        except Exception as e:
            logger.error(f"Error appending transcript to GCP: {e}")
            raise

    async def _save_metadata(self, file_path: Path, metadata: Dict[str, Any]) -> None:
        """Save metadata as JSON alongside file."""
        try:
            import json

            metadata_path = file_path.parent / f"{file_path.stem}_metadata.json"
            metadata_json = json.dumps(metadata, indent=2, default=str)

            async with aiofiles.open(metadata_path, "w") as f:
                await f.write(metadata_json)

            logger.info(f"Metadata saved: {metadata_path}")

        except Exception as e:
            logger.warning(f"Error saving metadata: {e}")

    async def get_file(self, file_path: str) -> Optional[bytes]:
        """
        Retrieve file from storage.

        Args:
            file_path: Path to file

        Returns:
            File content or None if not found
        """
        try:
            if self.config.use_gcp and self.gcs_storage:
                return await self._get_from_gcp(file_path)
            else:
                return await self._get_from_local(file_path)

        except Exception as e:
            logger.error(f"Error retrieving file: {e}")
            return None

    async def _get_from_local(self, file_path: str) -> Optional[bytes]:
        """Get file from local filesystem."""
        try:
            full_path = Path(self.config.local_storage_path) / file_path

            if not full_path.exists():
                logger.warning(f"File not found locally: {full_path}")
                return None

            async with aiofiles.open(full_path, "rb") as f:
                content = await f.read()

            return content

        except Exception as e:
            logger.error(f"Error reading local file: {e}")
            return None

    async def _get_from_gcp(self, file_path: str) -> Optional[bytes]:
        """Get file from GCP bucket."""
        try:
            blob = self.gcs_storage.bucket.blob(file_path)

            if not blob.exists():
                logger.warning(f"File not found in GCS: {file_path}")
                return None

            content = blob.download_as_bytes()
            return content

        except Exception as e:
            logger.error(f"Error reading from GCP: {e}")
            return None

    async def delete_file(self, file_path: str) -> bool:
        """
        Delete file from storage.

        Args:
            file_path: Path to file

        Returns:
            True if successful, False otherwise
        """
        try:
            if self.config.use_gcp and self.gcs_storage:
                return await self._delete_from_gcp(file_path)
            else:
                return await self._delete_from_local(file_path)

        except Exception as e:
            logger.error(f"Error deleting file: {e}")
            return False

    async def _delete_from_local(self, file_path: str) -> bool:
        """Delete local file."""
        try:
            full_path = Path(self.config.local_storage_path) / file_path

            if full_path.exists():
                await aiofiles.os.remove(full_path)
                logger.info(f"File deleted locally: {full_path}")
                return True

            return False

        except Exception as e:
            logger.error(f"Error deleting local file: {e}")
            return False

    async def _delete_from_gcp(self, file_path: str) -> bool:
        """Delete file from GCP bucket."""
        try:
            blob = self.gcs_storage.bucket.blob(file_path)

            if blob.exists():
                blob.delete()
                logger.info(f"File deleted from GCS: {file_path}")
                return True
            else:
                logger.warning(f"File not found in GCS for deletion: {file_path}")
                return False

        except Exception as e:
            logger.error(f"Error deleting from GCP: {e}")
            return False

    def get_storage_info(self) -> Dict[str, Any]:
        """Get storage configuration info."""
        return {
            "storage_type": "gcp" if (self.config.use_gcp and self.gcs_storage) else "local",
            "local_path": self.config.local_storage_path,
            "gcp_bucket": self.config.gcp_bucket if self.config.use_gcp else None,
            "gcp_enabled": self.config.use_gcp and self.gcs_storage is not None,
        }
