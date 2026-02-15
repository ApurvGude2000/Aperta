"""
GCS-based conversation storage service.
Stores conversations as JSON files in Google Cloud Storage.
"""
import json
from typing import List, Optional, Dict, Any
from datetime import datetime
from google.cloud import storage
from google.oauth2 import service_account
from config import settings
from utils.logger import setup_logger

logger = setup_logger(__name__)


class ConversationStorage:
    """Handle conversation storage in GCS bucket."""

    def __init__(self):
        """Initialize GCS client."""
        self.bucket_name = settings.gcp_bucket_name
        self.conversations_folder = "conversations/"

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
                logger.info(f"Conversation storage initialized: gs://{self.bucket_name}/{self.conversations_folder}")
            except Exception as e:
                logger.error(f"Failed to initialize GCS client: {e}")
                raise
        else:
            # For Cloud Run, use default credentials
            self.client = storage.Client(project=settings.gcp_project_id)
            self.bucket = self.client.bucket(self.bucket_name)
            logger.info(f"Conversation storage initialized with default credentials")

    def save_conversation(self, conversation_id: str, conversation_data: Dict[str, Any]) -> bool:
        """
        Save conversation to GCS as JSON file.

        Args:
            conversation_id: Unique conversation ID
            conversation_data: Conversation data dictionary

        Returns:
            bool: Success status
        """
        try:
            # Add metadata
            conversation_data['updated_at'] = datetime.utcnow().isoformat()

            # Create blob path
            blob_path = f"{self.conversations_folder}{conversation_id}.json"
            blob = self.bucket.blob(blob_path)

            # Upload as JSON
            blob.upload_from_string(
                json.dumps(conversation_data, indent=2),
                content_type='application/json'
            )

            logger.info(f"Saved conversation {conversation_id} to GCS")
            return True

        except Exception as e:
            logger.error(f"Failed to save conversation {conversation_id}: {e}")
            return False

    def get_conversation(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve conversation from GCS.

        Args:
            conversation_id: Conversation ID

        Returns:
            Conversation data or None
        """
        try:
            blob_path = f"{self.conversations_folder}{conversation_id}.json"
            blob = self.bucket.blob(blob_path)

            if not blob.exists():
                logger.warning(f"Conversation {conversation_id} not found in GCS")
                return None

            data = blob.download_as_text()
            conversation = json.loads(data)

            logger.info(f"Retrieved conversation {conversation_id} from GCS")
            return conversation

        except Exception as e:
            logger.error(f"Failed to get conversation {conversation_id}: {e}")
            return None

    def list_conversations(self, user_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List all conversations from GCS.

        Args:
            user_id: Optional user ID to filter conversations

        Returns:
            List of conversation metadata
        """
        try:
            blobs = self.bucket.list_blobs(prefix=self.conversations_folder)
            conversations = []

            for blob in blobs:
                # Skip folder markers
                if blob.name.endswith('/'):
                    continue

                # Download and parse conversation
                try:
                    data = blob.download_as_text()
                    conversation = json.loads(data)

                    # Filter by user_id if provided
                    if user_id and conversation.get('user_id') != user_id:
                        continue

                    # Add ID from filename
                    conversation_id = blob.name.replace(self.conversations_folder, '').replace('.json', '')
                    conversation['id'] = conversation_id

                    conversations.append(conversation)

                except Exception as e:
                    logger.warning(f"Failed to parse conversation {blob.name}: {e}")
                    continue

            # Sort by created_at (newest first)
            conversations.sort(key=lambda x: x.get('created_at', ''), reverse=True)

            logger.info(f"Listed {len(conversations)} conversations from GCS")
            return conversations

        except Exception as e:
            logger.error(f"Failed to list conversations: {e}")
            return []

    def delete_conversation(self, conversation_id: str) -> bool:
        """
        Delete conversation from GCS.

        Args:
            conversation_id: Conversation ID

        Returns:
            bool: Success status
        """
        try:
            blob_path = f"{self.conversations_folder}{conversation_id}.json"
            blob = self.bucket.blob(blob_path)

            if blob.exists():
                blob.delete()
                logger.info(f"Deleted conversation {conversation_id} from GCS")
                return True
            else:
                logger.warning(f"Conversation {conversation_id} not found for deletion")
                return False

        except Exception as e:
            logger.error(f"Failed to delete conversation {conversation_id}: {e}")
            return False

    def update_conversation(self, conversation_id: str, updates: Dict[str, Any]) -> bool:
        """
        Update existing conversation in GCS.

        Args:
            conversation_id: Conversation ID
            updates: Dictionary of fields to update

        Returns:
            bool: Success status
        """
        try:
            # Get existing conversation
            conversation = self.get_conversation(conversation_id)
            if not conversation:
                logger.error(f"Cannot update non-existent conversation {conversation_id}")
                return False

            # Update fields
            conversation.update(updates)
            conversation['updated_at'] = datetime.utcnow().isoformat()

            # Save back
            return self.save_conversation(conversation_id, conversation)

        except Exception as e:
            logger.error(f"Failed to update conversation {conversation_id}: {e}")
            return False


# Global instance
conversation_storage = ConversationStorage()
