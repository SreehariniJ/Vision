import logging
from typing import List, Dict, Any, Optional
from qdrant_client import AsyncQdrantClient
from qdrant_client.http import models as rest
from app.config import settings

logger = logging.getLogger(__name__)

class VectorStore:
    """Client for Qdrant vector database."""
    
    def __init__(self):
        self.client = AsyncQdrantClient(host=settings.QDRANT_HOST, port=settings.QDRANT_PORT)
        self.collection_name = settings.QDRANT_COLLECTION
        self.vector_size = 1024 # BGE-M3 dimension
        
    async def ensure_collection(self):
        """Ensure the collection exists in Qdrant."""
        try:
            collections_response = await self.client.get_collections()
            collections = [c.name for c in collections_response.collections]
            
            if self.collection_name not in collections:
                logger.info(f"Creating Qdrant collection: {self.collection_name}")
                await self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=rest.VectorParams(
                        size=self.vector_size,
                        distance=rest.Distance.COSINE
                    )
                )
                
                # Create payload index for document_id for efficient filtering
                await self.client.create_payload_index(
                    collection_name=self.collection_name,
                    field_name="document_id",
                    field_schema=rest.PayloadSchemaType.KEYWORD
                )
        except Exception as e:
            logger.error(f"Failed to ensure Qdrant collection: {e}")
            raise
            
    async def search(self, query_vector: List[float], limit: int = 10, document_ids: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """Search for similar vectors."""
        filter_params = None
        if document_ids:
            filter_params = rest.Filter(
                must=[
                    rest.FieldCondition(
                        key="document_id",
                        match=rest.MatchAny(any=document_ids)
                    )
                ]
            )
            
        try:
            search_result = await self.client.search(
                collection_name=self.collection_name,
                query_vector=query_vector,
                query_filter=filter_params,
                limit=limit,
                with_payload=True
            )
            
            return [
                {
                    "id": hit.id,
                    "score": hit.score,
                    "payload": hit.payload
                }
                for hit in search_result
            ]
        except Exception as e:
            logger.error(f"Vector search failed: {e}")
            return []

# Singleton instance
vector_store = VectorStore()
