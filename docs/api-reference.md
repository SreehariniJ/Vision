# API Reference

Interactive docs are available when the backend is running:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## OpenAI-Compatible Endpoints

- `GET /v1/models`
- `POST /v1/chat/completions`

OpenWebUI is configured to use `http://backend:8000/v1`.

## Document and Search Endpoints

The document/search routes are available under both `/v1` and `/api` for compatibility.

- `POST /v1/documents/upload`
- `GET /v1/documents/{document_id}/status`
- `POST /v1/search/`
- `POST /api/documents/upload`
- `GET /api/documents/{document_id}/status`
- `POST /api/search/`

Document status values:

- `queued`
- `processing`
- `indexed`
- `failed`

## System Endpoints

- `GET /api/health` - lightweight backend liveness
- `GET /api/ready` - dependency readiness across databases, model services, storage, and vLLM
