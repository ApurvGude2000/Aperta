"""
Embedding service using JINA AI embeddings for semantic search.
"""
import httpx
from typing import List, Optional
from config import settings
from utils.logger import setup_logger

logger = setup_logger(__name__)


class JINAEmbeddingService:
    """
    JINA AI Embedding Service for generating text embeddings.

    Uses JINA AI's embedding API to generate high-quality embeddings
    for semantic search across conversations.
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize JINA embedding service.

        Args:
            api_key: JINA AI API key (or use from settings)
        """
        self.api_key = api_key or getattr(settings, 'jina_api_key', None)
        self.base_url = "https://api.jina.ai/v1/embeddings"
        self.model = "jina-embeddings-v2-base-en"  # 768 dimensions
        self.dimension = 768

        if not self.api_key:
            logger.warning("JINA API key not configured. Embeddings will not work.")
        else:
            logger.info(f"JINA Embedding Service initialized with model: {self.model}")

    async def embed_text(self, text: str) -> Optional[List[float]]:
        """
        Generate embedding for a single text.

        Args:
            text: Text to embed

        Returns:
            Embedding vector (768 dimensions) or None on error
        """
        if not self.api_key:
            logger.error("JINA API key not configured")
            return None

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.base_url,
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "input": [text],
                        "model": self.model
                    },
                    timeout=30.0
                )

                if response.status_code == 200:
                    data = response.json()
                    embedding = data["data"][0]["embedding"]
                    logger.debug(f"Generated embedding: {len(embedding)} dimensions")
                    return embedding
                else:
                    logger.error(f"JINA API error: {response.status_code} - {response.text}")
                    return None

        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            return None

    async def embed_batch(self, texts: List[str]) -> List[Optional[List[float]]]:
        """
        Generate embeddings for multiple texts in batch.

        Args:
            texts: List of texts to embed

        Returns:
            List of embedding vectors (or None for failures)
        """
        if not self.api_key:
            logger.error("JINA API key not configured")
            return [None] * len(texts)

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.base_url,
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "input": texts,
                        "model": self.model
                    },
                    timeout=60.0
                )

                if response.status_code == 200:
                    data = response.json()
                    embeddings = [item["embedding"] for item in data["data"]]
                    logger.info(f"Generated {len(embeddings)} embeddings")
                    return embeddings
                else:
                    logger.error(f"JINA API error: {response.status_code} - {response.text}")
                    return [None] * len(texts)

        except Exception as e:
            logger.error(f"Error generating batch embeddings: {e}")
            return [None] * len(texts)


# Global embedding service instance
embedding_service = JINAEmbeddingService()
