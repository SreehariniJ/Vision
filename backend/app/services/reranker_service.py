import httpx
import logging
from typing import List, Dict, Any
from app.config import settings

logger = logging.getLogger(__name__)

class RerankerService:
    """Client for the internal BGE-Reranker service."""
    
    def __init__(self):
        self.base_url = settings.RERANKER_URL
        
    async def rerank(self, query: str, documents: List[str], top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Rerank a list of documents based on relevance to the query.
        Returns a list of dicts with 'index', 'text', and 'score'.
        """
        if not documents:
            return []

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.base_url}/rerank",
                    json={
                        "query": query,
                        "documents": documents,
                        "top_k": top_k
                    }
                )
                response.raise_for_status()
                data = response.json()
                return data["results"]
                
        except httpx.HTTPError as e:
            logger.error(f"Failed to rerank documents: {e}")
            # Fallback: if reranker fails, just return top_k documents with dummy scores
            logger.warning("Reranker failed, falling back to original order")
            return [
                {"index": i, "text": doc, "score": 1.0 - (i * 0.01)}
                for i, doc in enumerate(documents[:top_k])
            ]

# Singleton instance
reranker_service = RerankerService()
