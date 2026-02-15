"""
Storage service for managing audio files and transcriptions.
Supports both local filesystem and S3 cloud storage.
"""

import os
from pathlib import Path
from typing import Optional, Dict, Any
import logging
from datetime import datetime
import aiofiles
import aiofiles.os

logger = logging.getLogger(__name__)


class StorageConfig:
    """Storage configuration."""

    def __init__(
        self,
        local_storage_path: str = "./uploads",
        use_s3: bool = False,
        s3_bucket: Optional[str] = None,
        s3_region: Optional[str] = None,
        s3_access_key: Optional[str] = None,
        s3_secret_key: Optional[str] = None,
        s3_endpoint_url: Optional[str] = None,
    ):
        self.local_storage_path = local_storage_path
        self.use_s3 = use_s3
        self.s3_bucket = s3_bucket
        self.s3_region = s3_region
        self.s3_access_key = s3_access_key
        self.s3_secret_key = s3_secret_key
        self.s3_endpoint_url = s3_endpoint_url

        # Create local storage directory if it doesn't exist
        Path(self.local_storage_path).mkdir(parents=True, exist_ok=True)


class StorageService:
    """
    Unified storage service for audio files and transcriptions.

    Supports:
    - Local filesystem storage (development)
    - S3 cloud storage (production)
    - Automatic path organization
    - Metadata tracking
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
                use_s3=getattr(config, 'use_s3', False),
                s3_bucket=getattr(config, 's3_bucket_name', None),
                s3_region=getattr(config, 's3_region', 'us-east-1'),
                s3_access_key=getattr(config, 'aws_access_key_id', None),
                s3_secret_key=getattr(config, 'aws_secret_access_key', None),
                s3_endpoint_url=getattr(config, 's3_endpoint_url', None),
            )
        else:
            self.config = config

        self.s3_client = None

        if self.config.use_s3:
            self._init_s3()

        logger.info(
            f"StorageService initialized: "
            f"local={self.config.local_storage_path}, "
            f"s3={'enabled' if self.config.use_s3 else 'disabled'}"
        )

    def _init_s3(self):
        """Initialize S3 client."""
        try:
            import boto3

            self.s3_client = boto3.client(
                "s3",
                region_name=self.config.s3_region,
                aws_access_key_id=self.config.s3_access_key,
                aws_secret_access_key=self.config.s3_secret_key,
                endpoint_url=self.config.s3_endpoint_url,
            )
            logger.info(f"S3 client initialized: bucket={self.config.s3_bucket}")
        except Exception as e:
            logger.warning(f"Failed to initialize S3 client: {e}. Using local storage only.")
            self.config.use_s3 = False

    async def save_audio_file(
        self,
        file_content: bytes,
        conversation_id: str,
        filename: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Save audio file to storage.

        Args:
            file_content: Raw audio file bytes
            conversation_id: Conversation ID
            filename: Original filename
            metadata: Optional metadata

        Returns:
            Path/URL where file was saved
        """
        try:
            # Generate file path
            date_path = datetime.utcnow().strftime("%Y/%m/%d")
            file_path = f"{conversation_id}/{date_path}/{filename}"

            if self.config.use_s3 and self.s3_client:
                return await self._save_to_s3(file_content, file_path, metadata)
            else:
                return await self._save_to_local(file_content, file_path, metadata)

        except Exception as e:
            logger.error(f"Error saving audio file: {e}")
            raise

    async def _save_to_local(
        self,
        file_content: bytes,
        file_path: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Save file to local filesystem."""
        try:
            # Create directory structure
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

    async def _save_to_s3(
        self,
        file_content: bytes,
        file_path: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Save file to S3."""
        try:
            s3_key = f"audio/{file_path}"

            # Prepare S3 metadata
            s3_metadata = {
                "timestamp": datetime.utcnow().isoformat(),
                **(metadata or {}),
            }

            # Upload to S3
            self.s3_client.put_object(
                Bucket=self.config.s3_bucket,
                Key=s3_key,
                Body=file_content,
                Metadata={k: str(v) for k, v in s3_metadata.items()},
            )

            logger.info(f"Audio file saved to S3: s3://{self.config.s3_bucket}/{s3_key}")

            # Return S3 URL
            if self.config.s3_endpoint_url:
                return f"{self.config.s3_endpoint_url}/{self.config.s3_bucket}/{s3_key}"
            else:
                return f"s3://{self.config.s3_bucket}/{s3_key}"

        except Exception as e:
            logger.error(f"Error saving to S3: {e}")
            raise

    async def save_transcript(
        self,
        transcript_text: str,
        conversation_id: str,
        format: str = "txt",
    ) -> str:
        """
        Save transcript text to storage.

        Args:
            transcript_text: Formatted transcript text
            conversation_id: Conversation ID
            format: File format (txt, json, etc.)

        Returns:
            Path/URL where transcript was saved
        """
        try:
            filename = f"{conversation_id}_transcript.{format}"
            date_path = datetime.utcnow().strftime("%Y/%m/%d")
            file_path = f"{conversation_id}/{date_path}/{filename}"

            transcript_bytes = transcript_text.encode("utf-8")

            if self.config.use_s3 and self.s3_client:
                return await self._save_transcript_to_s3(transcript_bytes, file_path)
            else:
                return await self._save_transcript_local(transcript_bytes, file_path)

        except Exception as e:
            logger.error(f"Error saving transcript: {e}")
            raise

    async def _save_transcript_local(self, content: bytes, file_path: str) -> str:
        """Save transcript locally."""
        try:
            full_path = Path(self.config.local_storage_path) / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)

            async with aiofiles.open(full_path, "wb") as f:
                await f.write(content)

            logger.info(f"Transcript saved locally: {full_path}")
            return str(full_path)

        except Exception as e:
            logger.error(f"Error saving transcript locally: {e}")
            raise

    async def _save_transcript_to_s3(self, content: bytes, file_path: str) -> str:
        """Save transcript to S3."""
        try:
            s3_key = f"transcripts/{file_path}"

            self.s3_client.put_object(
                Bucket=self.config.s3_bucket,
                Key=s3_key,
                Body=content,
                ContentType="text/plain",
                Metadata={"timestamp": datetime.utcnow().isoformat()},
            )

            logger.info(f"Transcript saved to S3: s3://{self.config.s3_bucket}/{s3_key}")

            if self.config.s3_endpoint_url:
                return f"{self.config.s3_endpoint_url}/{self.config.s3_bucket}/{s3_key}"
            else:
                return f"s3://{self.config.s3_bucket}/{s3_key}"

        except Exception as e:
            logger.error(f"Error saving transcript to S3: {e}")
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
            if self.config.use_s3 and self.s3_client:
                return await self._get_from_s3(file_path)
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

    async def _get_from_s3(self, file_path: str) -> Optional[bytes]:
        """Get file from S3."""
        try:
            s3_key = f"audio/{file_path}"

            response = self.s3_client.get_object(Bucket=self.config.s3_bucket, Key=s3_key)
            content = response["Body"].read()

            return content

        except Exception as e:
            logger.error(f"Error reading from S3: {e}")
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
            if self.config.use_s3 and self.s3_client:
                return await self._delete_from_s3(file_path)
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

    async def _delete_from_s3(self, file_path: str) -> bool:
        """Delete file from S3."""
        try:
            s3_key = f"audio/{file_path}"

            self.s3_client.delete_object(Bucket=self.config.s3_bucket, Key=s3_key)
            logger.info(f"File deleted from S3: {s3_key}")

            return True

        except Exception as e:
            logger.error(f"Error deleting from S3: {e}")
            return False

    def get_storage_info(self) -> Dict[str, Any]:
        """Get storage configuration info."""
        return {
            "storage_type": "s3" if (self.config.use_s3 and self.s3_client) else "local",
            "local_path": self.config.local_storage_path,
            "s3_bucket": self.config.s3_bucket if self.config.use_s3 else None,
            "s3_enabled": self.config.use_s3 and self.s3_client is not None,
        }
