import logging
import os
from pathlib import Path
from typing import List, Union

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from sentence_transformers import SentenceTransformer

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("embedding-service")

app = FastAPI(title="BGE-M3 Embedding Service")

MODEL_NAME = os.environ.get("MODEL_NAME", "/models/bge-m3")
DEVICE = os.environ.get("DEVICE", "cuda")
BATCH_SIZE = int(os.environ.get("BATCH_SIZE", "32"))


def validate_runtime(model_name: str, device: str) -> None:
    if model_name.startswith("/") or model_name.startswith("./"):
        model_path = Path(model_name)
        if not model_path.exists():
            raise RuntimeError(
                f"Embedding model path does not exist: {model_path}. "
                "Check MODEL_ROOT in .env and the models/bge-m3 folder."
            )
        if not (model_path / "config.json").exists():
            raise RuntimeError(f"Embedding model is missing config.json: {model_path}")
        if not any(model_path.rglob("*.safetensors")) and not any(model_path.rglob("*.bin")):
            raise RuntimeError(f"Embedding model has no weight files: {model_path}")

    if device.startswith("cuda"):
        import torch

        if not torch.cuda.is_available():
            raise RuntimeError(
                "Embedding service was configured for CUDA, but torch.cuda.is_available() is false."
            )


def load_model() -> SentenceTransformer:
    logger.info("Loading embedding model: model=%s device=%s batch_size=%s", MODEL_NAME, DEVICE, BATCH_SIZE)
    validate_runtime(MODEL_NAME, DEVICE)
    try:
        loaded_model = SentenceTransformer(MODEL_NAME, device=DEVICE)
    except Exception as exc:
        logger.exception("Embedding model load failed")
        raise RuntimeError(f"Failed to load embedding model {MODEL_NAME!r}: {exc}") from exc
    logger.info("Embedding model loaded successfully")
    return loaded_model


model = load_model()


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

    embeddings = model.encode(inputs, batch_size=BATCH_SIZE, normalize_embeddings=True)

    data = [
        EmbeddingData(embedding=embedding.tolist(), index=index)
        for index, embedding in enumerate(embeddings)
    ]

    total_chars = sum(len(text) for text in inputs)
    est_tokens = total_chars // 4

    return EmbeddingResponse(
        data=data,
        model=request.model,
        usage={"prompt_tokens": est_tokens, "total_tokens": est_tokens},
    )
