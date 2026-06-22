import logging
from typing import List, Dict, Any, Optional
import httpx
import json

from app.services.embedding_service import embedding_service
from app.services.reranker_service import reranker_service
from app.services.vector_store import vector_store
from app.services.graph_store import graph_store
from app.config import settings

logger = logging.getLogger(__name__)

class RAGPipeline:
    """Core Retrieval-Augmented Generation pipeline."""
    
    def __init__(self):
        self.vllm_base_url = settings.VLLM_BASE_URL
        
    async def extract_keywords(self, query: str) -> List[str]:
        """Simple keyword extraction for graph search (could use an LLM or NLP library)."""
        stop_words = {"what", "is", "the", "a", "an", "in", "on", "at", "to", "for", "of", "and", "or", "how", "why"}
        words = [w.lower().strip("?,.!") for w in query.split()]
        keywords = [w for w in words if w and w not in stop_words and len(w) > 2]
        return keywords[:5] # Limit to top 5 keywords

    async def retrieve_context(self, query: str, limit: int = 10) -> List[str]:
        """
        Execute hybrid search (Vector + Graph), merge, and rerank.
        """
        logger.info(f"Retrieving context for query: {query}")
        
        # 1. Get query embeddings
        query_embeddings = await embedding_service.get_embeddings(query)
        if not query_embeddings:
            logger.warning("Failed to get query embedding")
            return []
        
        query_vector = query_embeddings[0]
        
        # 2. Extract keywords for graph search
        keywords = await self.extract_keywords(query)
        
        # 3. Parallel retrieval (Simulated here sequentially for clarity, in production use asyncio.gather)
        # Vector Search
        vector_results = await vector_store.search(query_vector, limit=limit)
        vector_texts = [hit["payload"].get("text", "") for hit in vector_results if hit.get("payload")]
        
        # Graph Search
        graph_results = await graph_store.search_related_entities(keywords, limit=3)
        graph_texts = []
        for record in graph_results:
            chunks = record.get("chunk_texts", [])
            graph_texts.extend(chunks)
            # Also add entity relationship context
            entity_name = record.get("entity_name")
            related = record.get("related_entities", [])
            if related:
                graph_texts.append(f"Knowledge Graph Context: {entity_name} is related to {', '.join(related)}.")
        
        # 4. Merge and deduplicate
        all_texts = list(set(vector_texts + graph_texts))
        
        if not all_texts:
            return []
            
        # 5. Rerank
        reranked_results = await reranker_service.rerank(query, all_texts, top_k=5)
        
        return [res["text"] for res in reranked_results]

    async def chat_completion(self, request_data: dict, stream: bool = False):
        """
        OpenAI-compatible chat completion endpoint handler with RAG augmentation.
        """
        messages = request_data.get("messages", [])
        
        # Extract the latest user query
        latest_query = ""
        for msg in reversed(messages):
            if msg.get("role") == "user":
                content = msg.get("content")
                if isinstance(content, str):
                    latest_query = content
                elif isinstance(content, list):
                    # Handle multimodal content (image + text)
                    for item in content:
                        if item.get("type") == "text":
                            latest_query += item.get("text", "") + " "
                break
                
        # Retrieve context if there's a text query
        context_texts = []
        if latest_query.strip():
            context_texts = await self.retrieve_context(latest_query)
            
        # Augment the prompt with retrieved context
        if context_texts:
            context_str = "\n\n---\n\n".join(context_texts)
            system_prompt = f"""You are Vision, a highly capable AI assistant for VSSC.
Use the following retrieved context to answer the user's question. 
If the answer is not contained in the context, say "I don't have enough information to answer that based on the provided documents," but still try to provide a helpful response if it's general knowledge.

<context>
{context_str}
</context>"""
            
            # Insert or update system prompt
            if messages and messages[0].get("role") == "system":
                messages[0]["content"] = system_prompt + "\n\nOriginal System Prompt:\n" + messages[0]["content"]
            else:
                messages.insert(0, {"role": "system", "content": system_prompt})
                
        # Forward the augmented request to vLLM
        request_data["messages"] = messages
        request_data["stream"] = stream
        request_data.setdefault("max_tokens", 8192)
        
        url = f"{self.vllm_base_url}/chat/completions"

        if stream:
            async def stream_generator():
                async with httpx.AsyncClient(timeout=120.0) as client:
                    async with client.stream("POST", url, json=request_data) as response:
                        response.raise_for_status()
                        async for chunk in response.aiter_raw():
                            yield chunk

            return stream_generator()

        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(url, json=request_data)
            response.raise_for_status()
            return response.json()

# Singleton instance
rag_pipeline = RAGPipeline()
