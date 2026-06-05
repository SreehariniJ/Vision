import os
from typing import List, Dict, Any
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sentence_transformers import CrossEncoder

app = FastAPI(title="BGE-Reranker Service")

# Configuration
MODEL_NAME = os.environ.get("MODEL_NAME", "BAAI/bge-reranker-v2-m3")
DEVICE = os.environ.get("DEVICE", "cuda")
TOP_K = int(os.environ.get("TOP_K", "5"))

print(f"Loading model {MODEL_NAME} on {DEVICE}...")
model = CrossEncoder(MODEL_NAME, max_length=1024, device=DEVICE)
print("Model loaded successfully.")

class RerankRequest(BaseModel):
    query: str
    documents: List[str]
    top_k: int = TOP_K

class RerankResult(BaseModel):
    index: int
    text: str
    score: float

class RerankResponse(BaseModel):
    results: List[RerankResult]

@app.get("/health")
def health_check():
    return {"status": "ok", "model": MODEL_NAME, "device": DEVICE}

@app.post("/rerank", response_model=RerankResponse)
async def rerank_documents(request: RerankRequest):
    if not request.query or not request.documents:
        raise HTTPException(status_code=400, detail="Query and documents must be provided")

    pairs = [[request.query, doc] for doc in request.documents]
    scores = model.predict(pairs)
    
    # Combine scores with documents and original indices
    results = [
        {"index": i, "text": request.documents[i], "score": float(scores[i])}
        for i in range(len(request.documents))
    ]
    
    # Sort by score descending
    results.sort(key=lambda x: x["score"], reverse=True)
    
    # Take top K
    top_results = results[:request.top_k]
    
    return RerankResponse(results=[RerankResult(**res) for res in top_results])
