"""
GCS-based transcript storage service.
Reads transcript files from GCS bucket's transcripts/ folder.
"""
import json
from typing import List, Optional, Dict, Any
from datetime import datetime
from google.cloud import storage
from google.oauth2 import service_account
from config import settings
from utils.logger import setup_logger

logger = setup_logger(__name__)


class TranscriptStorage:
    """Handle reading transcripts from GCS bucket."""

    def __init__(self):
        """Initialize GCS client."""
        self.bucket_name = settings.gcp_bucket_name
        self.transcripts_folder = "transcripts/"

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
            logger.info(f"Transcript storage initialized: gs://{self.bucket_name}/{self.transcripts_folder}")
        except Exception as e:
            logger.error(f"Failed to initialize GCS client: {e}")
            raise

    def list_transcripts(self, user_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List all transcript files from GCS transcripts folder.

        Args:
            user_id: Optional user ID to filter (not used for now)

        Returns:
            List of transcript metadata
        """
        try:
            blobs = self.bucket.list_blobs(prefix=self.transcripts_folder)
            transcripts = []

            for blob in blobs:
                # Skip folder markers
                if blob.name.endswith('/'):
                    continue

                # Get file info
                file_name = blob.name.replace(self.transcripts_folder, '')

                # Create transcript metadata
                transcript_info = {
                    "id": file_name.replace('.txt', '').replace('.json', ''),
                    "title": file_name,
                    "file_name": file_name,
                    "gcs_path": blob.name,
                    "size": blob.size,
                    "created_at": blob.time_created.isoformat() if blob.time_created else None,
                    "updated_at": blob.updated.isoformat() if blob.updated else None,
                    "status": "active",
                    "user_id": user_id or "default_user"
                }

                transcripts.append(transcript_info)

            # Sort by created time (newest first)
            transcripts.sort(key=lambda x: x.get('created_at', ''), reverse=True)

            logger.info(f"Found {len(transcripts)} transcripts in GCS")
            return transcripts

        except Exception as e:
            logger.error(f"Failed to list transcripts: {e}")
            return []

    def get_transcript(self, transcript_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific transcript by ID.

        Args:
            transcript_id: Transcript ID (filename without extension)

        Returns:
            Transcript data with content
        """
        try:
            # Try different file extensions
            for ext in ['.txt', '.json', '']:
                blob_path = f"{self.transcripts_folder}{transcript_id}{ext}"
                blob = self.bucket.blob(blob_path)

                if blob.exists():
                    content = blob.download_as_text()

                    # Parse JSON if it's a JSON file
                    if ext == '.json':
                        try:
                            data = json.loads(content)
                            if isinstance(data, dict):
                                data['id'] = transcript_id
                                data['file_name'] = f"{transcript_id}{ext}"
                                data['transcript'] = data.get('transcript', content)
                                return data
                        except json.JSONDecodeError:
                            pass

                    # Return as plain text transcript
                    return {
                        "id": transcript_id,
                        "title": f"{transcript_id}{ext}",
                        "file_name": f"{transcript_id}{ext}",
                        "transcript": content,
                        "gcs_path": blob_path,
                        "size": blob.size,
                        "created_at": blob.time_created.isoformat() if blob.time_created else None,
                        "updated_at": blob.updated.isoformat() if blob.updated else None,
                        "status": "active",
                        "user_id": "default_user"
                    }

            logger.warning(f"Transcript {transcript_id} not found in GCS")
            return None

        except Exception as e:
            logger.error(f"Failed to get transcript {transcript_id}: {e}")
            return None

    def get_transcript_content(self, transcript_id: str) -> Optional[str]:
        """
        Get just the transcript content/text.

        Args:
            transcript_id: Transcript ID

        Returns:
            Transcript text content
        """
        transcript = self.get_transcript(transcript_id)
        if transcript:
            return transcript.get('transcript', '')
        return None

    def upload_transcript(self, file_name: str, content: str) -> bool:
        """
        Upload a new transcript to GCS.

        Args:
            file_name: Name of the transcript file
            content: Transcript content

        Returns:
            Success status
        """
        try:
            blob_path = f"{self.transcripts_folder}{file_name}"
            blob = self.bucket.blob(blob_path)

            blob.upload_from_string(
                content,
                content_type='text/plain' if file_name.endswith('.txt') else 'application/json'
            )

            logger.info(f"Uploaded transcript {file_name} to GCS")
            return True

        except Exception as e:
            logger.error(f"Failed to upload transcript {file_name}: {e}")
            return False


# Global instance
transcript_storage = TranscriptStorage()
