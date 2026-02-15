"""
Elasticsearch service for semantic search with vector embeddings.
"""
from typing import List, Dict, Any, Optional
from datetime import datetime
from elasticsearch import AsyncElasticsearch
from config import settings
from utils.logger import setup_logger
from services.embeddings import embedding_service

logger = setup_logger(__name__)


class ElasticsearchService:
    """
    Elasticsearch service for semantic conversation search.

    Uses JINA embeddings for vector similarity search across conversations.
    """

    def __init__(self):
        """Initialize Elasticsearch client."""
        self.es_host = getattr(settings, 'elasticsearch_host', 'http://localhost:9200')
        self.es_user = getattr(settings, 'elasticsearch_user', 'elastic')
        self.es_password = getattr(settings, 'elasticsearch_password', None)
        self.index_name = "aperta_conversations"

        # Initialize client with longer timeouts
        if self.es_password:
            self.client = AsyncElasticsearch(
                [self.es_host],
                basic_auth=(self.es_user, self.es_password),
                request_timeout=30,
                max_retries=3,
                retry_on_timeout=True
            )
        else:
            self.client = AsyncElasticsearch(
                [self.es_host],
                request_timeout=30,
                max_retries=3,
                retry_on_timeout=True
            )

        logger.info(f"Elasticsearch service initialized: {self.es_host}")

    async def create_index(self):
        """
        Create Elasticsearch index with vector field mapping.
        """
        try:
            # Check if index exists
            exists = await self.client.indices.exists(index=self.index_name)

            if exists:
                logger.info(f"Index {self.index_name} already exists")
                return True

            # Create index with mapping
            mapping = {
                "settings": {
                    "number_of_shards": 1,
                    "number_of_replicas": 0  # Single-node development
                },
                "mappings": {
                    "properties": {
                        "conversation_id": {"type": "keyword"},
                        "user_id": {"type": "keyword"},
                        "title": {"type": "text"},
                        "transcript": {"type": "text"},
                        "summary": {"type": "text"},
                        "embedding": {
                            "type": "dense_vector",
                            "dims": 768,
                            "index": True,
                            "similarity": "cosine"
                        },
                        "people": {"type": "keyword"},
                        "topics": {"type": "keyword"},
                        "companies": {"type": "keyword"},
                        "event_name": {"type": "keyword"},
                        "sentiment": {"type": "keyword"},
                        "created_at": {"type": "date"},
                        "duration_minutes": {"type": "integer"}
                    }
                }
            }

            await self.client.indices.create(index=self.index_name, body=mapping)
            logger.info(f"Created index: {self.index_name}")
            return True

        except Exception as e:
            logger.error(f"Error creating index: {e}")
            return False

    async def index_conversation(
        self,
        conversation_id: str,
        user_id: str,
        transcript: str,
        metadata: Dict[str, Any]
    ) -> bool:
        """
        Index a conversation with its embedding.

        Args:
            conversation_id: Unique conversation ID
            user_id: User who owns the conversation
            transcript: Full conversation transcript
            metadata: Additional metadata (title, people, topics, etc.)

        Returns:
            True if successful, False otherwise
        """
        try:
            # Generate embedding for transcript
            logger.info(f"Generating embedding for conversation {conversation_id}")
            embedding = await embedding_service.embed_text(transcript)

            if not embedding:
                logger.error(f"Failed to generate embedding for {conversation_id}")
                return False

            # Prepare document
            doc = {
                "conversation_id": conversation_id,
                "user_id": user_id,
                "transcript": transcript,
                "embedding": embedding,
                "title": metadata.get("title", ""),
                "summary": metadata.get("summary", ""),
                "people": metadata.get("people", []),
                "topics": metadata.get("topics", []),
                "companies": metadata.get("companies", []),
                "event_name": metadata.get("event_name", ""),
                "sentiment": metadata.get("sentiment", "neutral"),
                "created_at": metadata.get("created_at", datetime.utcnow().isoformat()),
                "duration_minutes": metadata.get("duration_minutes", 0)
            }

            # Index document
            await self.client.index(
                index=self.index_name,
                id=conversation_id,
                document=doc
            )

            logger.info(f"Indexed conversation {conversation_id}")
            return True

        except Exception as e:
            logger.error(f"Error indexing conversation: {e}")
            return False

    async def search_conversations(
        self,
        query: str,
        user_id: str,
        max_results: int = 10,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search conversations using semantic similarity.

        Args:
            query: Search query
            user_id: User ID for filtering
            max_results: Maximum number of results
            filters: Optional filters (topics, people, sentiment, etc.)

        Returns:
            List of matching conversations with scores
        """
        try:
            # Generate query embedding
            print(f"      [ELASTICSEARCH] Searching for: '{query}'")
            print(f"      [ELASTICSEARCH] ES host: {self.es_host}, index: {self.index_name}")
            logger.info(f"Searching conversations for: {query}")
            print(f"      [ELASTICSEARCH] Generating embedding via JINA...")
            query_embedding = await embedding_service.embed_text(query)
            print(f"      [ELASTICSEARCH] Embedding generated: {query_embedding is not None}, length: {len(query_embedding) if query_embedding else 0}")

            if not query_embedding:
                logger.error("Failed to generate query embedding")
                return []

            # Build search query
            search_body = {
                "knn": {
                    "field": "embedding",
                    "query_vector": query_embedding,
                    "k": max_results,
                    "num_candidates": max_results * 10,
                    "filter": {
                        "term": {"user_id": user_id}
                    }
                },
                "_source": [
                    "conversation_id", "title", "summary", "transcript",
                    "people", "topics", "companies", "event_name",
                    "sentiment", "created_at", "duration_minutes"
                ]
            }

            # Add additional filters
            if filters:
                filter_clauses = [{"term": {"user_id": user_id}}]

                if "topics" in filters:
                    filter_clauses.append({"terms": {"topics": filters["topics"]}})
                if "people" in filters:
                    filter_clauses.append({"terms": {"people": filters["people"]}})
                if "sentiment" in filters:
                    filter_clauses.append({"term": {"sentiment": filters["sentiment"]}})

                search_body["knn"]["filter"] = {"bool": {"must": filter_clauses}}

            # Execute search
            response = await self.client.search(
                index=self.index_name,
                body=search_body
            )

            # Process results
            results = []
            for hit in response["hits"]["hits"]:
                result = hit["_source"]
                result["relevance_score"] = hit["_score"]

                # Truncate transcript for preview
                if len(result.get("transcript", "")) > 500:
                    result["excerpt"] = result["transcript"][:500] + "..."
                else:
                    result["excerpt"] = result.get("transcript", "")

                results.append(result)

            logger.info(f"Found {len(results)} matching conversations")
            return results

        except Exception as e:
            print(f"      [ELASTICSEARCH] SEARCH ERROR: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            logger.error(f"Error searching conversations: {e}")
            return []

    async def delete_conversation(self, conversation_id: str) -> bool:
        """
        Delete a conversation from the index.

        Args:
            conversation_id: Conversation ID to delete

        Returns:
            True if successful, False otherwise
        """
        try:
            await self.client.delete(index=self.index_name, id=conversation_id)
            logger.info(f"Deleted conversation {conversation_id}")
            return True
        except Exception as e:
            logger.error(f"Error deleting conversation: {e}")
            return False

    async def close(self):
        """Close Elasticsearch client."""
        await self.client.close()


# Global Elasticsearch service instance
es_service = ElasticsearchService()
