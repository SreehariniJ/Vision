import logging
import os
from pathlib import Path
from typing import Any, Dict, List

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sentence_transformers import CrossEncoder

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("reranker-service")

app = FastAPI(title="BGE-Reranker Service")

MODEL_NAME = os.environ.get("MODEL_NAME", "/models/bge-reranker-v2-m3")
DEVICE = os.environ.get("DEVICE", "cuda")
TOP_K = int(os.environ.get("TOP_K", "5"))


def validate_runtime(model_name: str, device: str) -> None:
    if model_name.startswith("/") or model_name.startswith("./"):
        model_path = Path(model_name)
        if not model_path.exists():
            raise RuntimeError(
                f"Reranker model path does not exist: {model_path}. "
                "Check MODEL_ROOT in .env and the models/bge-reranker-v2-m3 folder."
            )
        if not (model_path / "config.json").exists():
            raise RuntimeError(f"Reranker model is missing config.json: {model_path}")
        if not any(model_path.rglob("*.safetensors")) and not any(model_path.rglob("*.bin")):
            raise RuntimeError(f"Reranker model has no weight files: {model_path}")

    if device.startswith("cuda"):
        import torch

        if not torch.cuda.is_available():
            raise RuntimeError(
                "Reranker service was configured for CUDA, but torch.cuda.is_available() is false."
            )


def load_model() -> CrossEncoder:
    logger.info("Loading reranker model: model=%s device=%s top_k=%s", MODEL_NAME, DEVICE, TOP_K)
    validate_runtime(MODEL_NAME, DEVICE)
    try:
        loaded_model = CrossEncoder(MODEL_NAME, max_length=1024, device=DEVICE)
    except Exception as exc:
        logger.exception("Reranker model load failed")
        raise RuntimeError(f"Failed to load reranker model {MODEL_NAME!r}: {exc}") from exc
    logger.info("Reranker model loaded successfully")
    return loaded_model


model = load_model()


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

    pairs = [[request.query, document] for document in request.documents]
    scores = model.predict(pairs)

    results: List[Dict[str, Any]] = [
        {"index": index, "text": request.documents[index], "score": float(scores[index])}
        for index in range(len(request.documents))
    ]

    results.sort(key=lambda item: item["score"], reverse=True)

    return RerankResponse(results=[RerankResult(**result) for result in results[: request.top_k]])
