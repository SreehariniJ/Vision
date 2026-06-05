from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional

from app.services.embedding_service import embedding_service
from app.services.vector_store import vector_store
from app.services.graph_store import graph_store
from app.services.rag_pipeline import rag_pipeline

router = APIRouter()

class SearchRequest(BaseModel):
    query: str
    limit: int = 10
    document_ids: Optional[List[str]] = None

class SearchResponse(BaseModel):
    results: List[str]

@router.post("/", response_model=SearchResponse)
async def hybrid_search(request: SearchRequest):
    """
    Perform hybrid search using vector DB and knowledge graph.
    """
    try:
        if not request.query.strip():
            raise HTTPException(status_code=400, detail="Query cannot be empty")
            
        # Use the pipeline's retrieve_context which already does hybrid + rerank
        results = await rag_pipeline.retrieve_context(request.query, limit=request.limit)
        
        return SearchResponse(results=results)
    except Exception as e:
        import logging
        logging.error(f"Search error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
