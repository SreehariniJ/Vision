import os
import time
from typing import List, Union
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from sentence_transformers import SentenceTransformer

app = FastAPI(title="BGE-M3 Embedding Service")

# Configuration
MODEL_NAME = os.environ.get("MODEL_NAME", "BAAI/bge-m3")
DEVICE = os.environ.get("DEVICE", "cuda")
BATCH_SIZE = int(os.environ.get("BATCH_SIZE", "32"))

print(f"Loading model {MODEL_NAME} on {DEVICE}...")
model = SentenceTransformer(MODEL_NAME, device=DEVICE)
print("Model loaded successfully.")

class EmbeddingRequest(BaseModel):
    input: Union[str, List[str]]
    model: str = Field(default=MODEL_NAME)

class EmbeddingData(BaseModel):
    object: str = "embedding"
    embedding: List[float]
    index: int

class EmbeddingResponse(BaseModel):
    object: str = "list"
    data: List[EmbeddingData]
    model: str
    usage: dict

@app.get("/health")
def health_check():
    return {"status": "ok", "model": MODEL_NAME, "device": DEVICE}

@app.post("/v1/embeddings", response_model=EmbeddingResponse)
async def create_embeddings(request: EmbeddingRequest):
    inputs = request.input if isinstance(request.input, list) else [request.input]
    
    if not inputs:
        raise HTTPException(status_code=400, detail="Input cannot be empty")

    start_time = time.time()
    embeddings = model.encode(inputs, batch_size=BATCH_SIZE, normalize_embeddings=True)
    
    data = []
    for i, emb in enumerate(embeddings):
        data.append(EmbeddingData(
            embedding=emb.tolist(),
            index=i
        ))
        
    # Calculate rough token usage (not exact, but required for OpenAI compat)
    total_chars = sum(len(text) for text in inputs)
    est_tokens = total_chars // 4

    return EmbeddingResponse(
        data=data,
        model=request.model,
        usage={"prompt_tokens": est_tokens, "total_tokens": est_tokens}
    )
