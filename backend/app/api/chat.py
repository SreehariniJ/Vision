import json
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import StreamingResponse

from app.services.rag_pipeline import rag_pipeline

router = APIRouter()

@router.post("/completions")
async def chat_completions(request: Request):
    """
    OpenAI-compatible chat completions endpoint with RAG.
    Intercepts the request, retrieves context, augments the prompt, 
    and forwards to vLLM.
    """
    try:
        body = await request.json()
        stream = body.get("stream", False)
        
        # Determine if we should handle it as a streaming request or not
        if stream:
            generator = await rag_pipeline.chat_completion(body, stream=True)
            return StreamingResponse(generator, media_type="text/event-stream")
        else:
            response_json = await rag_pipeline.chat_completion(body, stream=False)
            return response_json
            
    except Exception as e:
        import logging
        logging.error(f"Chat completion error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
