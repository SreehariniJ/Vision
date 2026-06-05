import httpx
import logging
from typing import List, Union
from app.config import settings

logger = logging.getLogger(__name__)

class EmbeddingService:
    """Client for the internal BGE-M3 embedding service."""
    
    def __init__(self):
        self.base_url = settings.EMBEDDING_URL
        
    async def get_embeddings(self, texts: Union[str, List[str]]) -> List[List[float]]:
        """
        Get embeddings for a list of texts using the internal embedding service.
        """
        if isinstance(texts, str):
            texts = [texts]
            
        if not texts:
            return []

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.base_url}/v1/embeddings",
                    json={"input": texts, "model": "BAAI/bge-m3"}
                )
                response.raise_for_status()
                data = response.json()
                
                # Extract embeddings and sort by index to ensure original order
                embeddings_data = sorted(data["data"], key=lambda x: x["index"])
                return [item["embedding"] for item in embeddings_data]
                
        except httpx.HTTPError as e:
            logger.error(f"Failed to get embeddings: {e}")
            raise Exception(f"Embedding service error: {e}")

# Singleton instance
embedding_service = EmbeddingService()
