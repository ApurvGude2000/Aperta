"""
Conversation Retrieval Agent - Searches conversations using vector similarity.
Updated to use Elasticsearch with JINA embeddings for real semantic search.
"""
from typing import Dict, Any, List, Optional
from services.elasticsearch_service import es_service
from utils.logger import setup_logger

logger = setup_logger(__name__)


class ConversationRetrievalAgent:
    """
    Conversation Retrieval Agent - Search conversations using semantic similarity.

    Purpose: Search conversations and return relevant excerpts.
    When Called: As determined by Query Router, for Q&A system.
    Implementation: Elasticsearch with JINA embeddings for vector search.
    """

    def __init__(self):
        """Initialize Conversation Retrieval Agent."""
        self.name = "conversation_retrieval"
        self.description = "Searches conversations using semantic vector similarity"
        logger.info("Conversation Retrieval Agent initialized")

    async def execute(
        self,
        user_question: str,
        user_id: str,
        max_results: int = 5,
        filters: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Search conversations for relevant excerpts.

        Args:
            user_question: User's search query
            user_id: User identifier for filtering
            max_results: Maximum number of results to return
            filters: Optional filters (topics, people, sentiment, etc.)

        Returns:
            Dict with search results
        """
        try:
            logger.info(f"Searching conversations for: {user_question}")

            # Use Elasticsearch service for semantic search
            results = await es_service.search_conversations(
                query=user_question,
                user_id=user_id,
                max_results=max_results,
                filters=filters
            )

            logger.info(f"Found {len(results)} conversation excerpts")

            return {
                "results": results,
                "total_found": len(results),
                "query": user_question
            }

        except Exception as e:
            logger.error(f"Conversation retrieval error: {e}")
            return {
                "results": [],
                "total_found": 0,
                "query": user_question,
                "error": str(e)
            }
