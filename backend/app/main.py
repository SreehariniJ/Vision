import logging
from typing import Any, Dict

import httpx
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from redis import Redis
from sqlalchemy import text

from app.config import settings
from app.core.database import engine

logging.basicConfig(
    level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(title=settings.PROJECT_NAME, openapi_url=f"{settings.API_V1_STR}/openapi.json")

if settings.CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


@app.get("/api/health")
async def health_check() -> dict:
    """Lightweight liveness check."""
    return {"status": "ok", "project": settings.PROJECT_NAME}


def _vllm_health_url() -> str:
    base_url = settings.VLLM_BASE_URL.rstrip("/")
    if base_url.endswith("/v1"):
        base_url = base_url[:-3]
    return f"{base_url}/health"


async def _check_http(name: str, url: str, results: Dict[str, Any]) -> None:
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            response = await client.get(url)
            response.raise_for_status()
        results[name] = {"status": "ok", "url": url}
    except Exception as exc:
        results[name] = {"status": "error", "url": url, "detail": str(exc)}


@app.get("/api/ready")
async def readiness_check() -> JSONResponse:
    """Dependency readiness check for operators and evaluators."""
    checks: Dict[str, Any] = {}

    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        checks["mysql"] = {"status": "ok"}
    except Exception as exc:
        checks["mysql"] = {"status": "error", "detail": str(exc)}

    try:
        redis_client = Redis.from_url(settings.REDIS_URL, socket_connect_timeout=3, socket_timeout=3)
        redis_client.ping()
        checks["redis"] = {"status": "ok"}
    except Exception as exc:
        checks["redis"] = {"status": "error", "detail": str(exc)}

    try:
        from app.services.minio_service import minio_service

        minio_service.client.bucket_exists(minio_service.bucket_name)
        checks["minio"] = {"status": "ok", "bucket": minio_service.bucket_name}
    except Exception as exc:
        checks["minio"] = {"status": "error", "detail": str(exc)}

    try:
        from app.services.graph_store import graph_store

        driver = await graph_store.get_driver()
        await driver.verify_connectivity()
        checks["neo4j"] = {"status": "ok"}
    except Exception as exc:
        checks["neo4j"] = {"status": "error", "detail": str(exc)}

    await _check_http("qdrant", f"http://{settings.QDRANT_HOST}:{settings.QDRANT_PORT}/readyz", checks)
    await _check_http("vllm", _vllm_health_url(), checks)
    await _check_http("embedding", f"{settings.EMBEDDING_URL.rstrip('/')}/health", checks)
    await _check_http("reranker", f"{settings.RERANKER_URL.rstrip('/')}/health", checks)
    await _check_http("docling", f"{settings.DOCLING_URL.rstrip('/')}/health", checks)
    await _check_http("ocr", f"{settings.OCR_URL.rstrip('/')}/health", checks)

    ready = all(check.get("status") == "ok" for check in checks.values())
    status_code = 200 if ready else 503
    return JSONResponse(status_code=status_code, content={"status": "ready" if ready else "not_ready", "checks": checks})


from app.api.router import api_router


@app.get("/v1/models")
async def get_models():
    return {
        "object": "list",
        "data": [{"id": "vision-model", "object": "model", "created": 1700000000, "owned_by": "vssc"}],
    }


app.include_router(api_router, prefix="/v1")
app.include_router(api_router, prefix="/api")


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.error("Global exception: %s", exc, exc_info=True)
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})
