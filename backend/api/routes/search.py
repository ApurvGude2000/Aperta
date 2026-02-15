"""
Search API endpoints for semantic conversation search.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import List, Dict, Optional, Any
from datetime import datetime

from db.session import get_db_session
from services.elasticsearch_service import es_service
from services.embeddings import embedding_service
from utils.logger import setup_logger

logger = setup_logger(__name__)
router = APIRouter(prefix="/search", tags=["Search"])


# Pydantic models
class SearchRequest(BaseModel):
    query: str
    user_id: str = "default_user"
    max_results: int = 10
    filters: Optional[Dict[str, Any]] = None


class SearchResult(BaseModel):
    conversation_id: str
    title: str
    excerpt: str
    relevance_score: float
    people: List[str]
    topics: List[str]
    companies: List[str]
    event_name: str
    sentiment: str
    created_at: str
    duration_minutes: int


class SearchResponse(BaseModel):
    results: List[SearchResult]
    total_found: int
    query: str
    execution_time_ms: float


class IndexConversationRequest(BaseModel):
    conversation_id: str
    user_id: str
    transcript: str
    metadata: Dict[str, Any]


class IndexResponse(BaseModel):
    success: bool
    conversation_id: str
    message: str


@router.post("/conversations", response_model=SearchResponse)
async def search_conversations(
    request: SearchRequest,
    db: AsyncSession = Depends(get_db_session)
) -> SearchResponse:
    """
    Search conversations using semantic similarity.

    Args:
        request: Search request with query and filters
        db: Database session

    Returns:
        Search results with relevance scores
    """
    import time
    start_time = time.time()

    try:
        logger.info(f"Search request: {request.query} (user: {request.user_id})")

        # Execute search
        search_results = await es_service.search_conversations(
            query=request.query,
            user_id=request.user_id,
            max_results=request.max_results,
            filters=request.filters
        )

        # Format results
        formatted_results = [
            SearchResult(
                conversation_id=r.get("conversation_id", ""),
                title=r.get("title", "Untitled"),
                excerpt=r.get("excerpt", ""),
                relevance_score=r.get("relevance_score", 0.0),
                people=r.get("people", []),
                topics=r.get("topics", []),
                companies=r.get("companies", []),
                event_name=r.get("event_name", ""),
                sentiment=r.get("sentiment", "neutral"),
                created_at=r.get("created_at", ""),
                duration_minutes=r.get("duration_minutes", 0)
            )
            for r in search_results
        ]

        execution_time = (time.time() - start_time) * 1000

        return SearchResponse(
            results=formatted_results,
            total_found=len(formatted_results),
            query=request.query,
            execution_time_ms=round(execution_time, 2)
        )

    except Exception as e:
        logger.error(f"Search error: {e}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@router.post("/index", response_model=IndexResponse)
async def index_conversation(
    request: IndexConversationRequest,
    db: AsyncSession = Depends(get_db_session)
) -> IndexResponse:
    """
    Index a conversation for semantic search.

    Args:
        request: Indexing request with conversation data
        db: Database session

    Returns:
        Indexing status
    """
    try:
        logger.info(f"Indexing conversation: {request.conversation_id}")

        success = await es_service.index_conversation(
            conversation_id=request.conversation_id,
            user_id=request.user_id,
            transcript=request.transcript,
            metadata=request.metadata
        )

        if success:
            return IndexResponse(
                success=True,
                conversation_id=request.conversation_id,
                message="Conversation indexed successfully"
            )
        else:
            raise HTTPException(
                status_code=500,
                detail="Failed to index conversation"
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Indexing error: {e}")
        raise HTTPException(status_code=500, detail=f"Indexing failed: {str(e)}")


@router.delete("/conversations/{conversation_id}")
async def delete_conversation(
    conversation_id: str,
    db: AsyncSession = Depends(get_db_session)
) -> Dict[str, Any]:
    """
    Delete a conversation from the search index.

    Args:
        conversation_id: Conversation ID to delete
        db: Database session

    Returns:
        Deletion status
    """
    try:
        success = await es_service.delete_conversation(conversation_id)

        if success:
            return {
                "success": True,
                "conversation_id": conversation_id,
                "message": "Conversation deleted from index"
            }
        else:
            raise HTTPException(
                status_code=500,
                detail="Failed to delete conversation"
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Deletion error: {e}")
        raise HTTPException(status_code=500, detail=f"Deletion failed: {str(e)}")


@router.post("/initialize")
async def initialize_search_index() -> Dict[str, Any]:
    """
    Initialize the Elasticsearch index.

    Returns:
        Initialization status
    """
    try:
        logger.info("Initializing search index")
        success = await es_service.create_index()

        if success:
            return {
                "success": True,
                "message": "Search index initialized successfully",
                "index_name": es_service.index_name
            }
        else:
            raise HTTPException(
                status_code=500,
                detail="Failed to initialize search index"
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Initialization error: {e}")
        raise HTTPException(status_code=500, detail=f"Initialization failed: {str(e)}")


@router.get("/health")
async def search_health() -> Dict[str, Any]:
    """
    Check search service health.

    Returns:
        Health status
    """
    try:
        # Check Elasticsearch connection
        info = await es_service.client.info()

        # Check embedding service
        embedding_configured = embedding_service.api_key is not None

        return {
            "elasticsearch": {
                "status": "connected",
                "cluster_name": info.get("cluster_name", "unknown"),
                "version": info.get("version", {}).get("number", "unknown")
            },
            "embedding_service": {
                "status": "configured" if embedding_configured else "not_configured",
                "model": embedding_service.model,
                "dimensions": embedding_service.dimension
            },
            "overall_status": "healthy" if embedding_configured else "degraded"
        }

    except Exception as e:
        logger.error(f"Health check error: {e}")
        return {
            "elasticsearch": {"status": "error", "message": str(e)},
            "embedding_service": {"status": "unknown"},
            "overall_status": "unhealthy"
        }
