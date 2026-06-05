# API Reference

The Vision backend provides a RESTful API built with FastAPI. Interactive documentation is automatically generated and available when the system is running.

## Accessing Interactive Docs

When the stack is running, navigate to:
* **Swagger UI:** `http://localhost:8000/docs`
* **ReDoc:** `http://localhost:8000/redoc`

## Core Endpoints

### Chat & Completion (OpenAI Compatible)

The backend implements OpenAI-compatible endpoints, allowing seamless integration with tools like OpenWebUI.

* **`POST /v1/chat/completions`**
  * Core RAG endpoint. Accepts standard OpenAI chat completion payloads.
  * Triggers hybrid search (vector + graph) and augments the prompt before generation.
  * Supports streaming (`stream: true`) via Server-Sent Events (SSE).
* **`GET /v1/models`**
  * Lists the currently active vLLM model profile.

### Document Management

* **`POST /api/documents/upload`**
  * Upload a file (PDF, DOCX, image) for ingestion.
  * Returns a task ID.
* **`GET /api/documents/{id}/status`**
  * Check the processing status of an uploaded document (`queued`, `processing`, `indexed`, `failed`).
* **`GET /api/documents`**
  * List all uploaded documents and their metadata.

### System

* **`GET /api/health`**
  * Basic health check. Returns `{"status": "ok"}` if the API is responding.
* **`GET /metrics`**
  * Exposes Prometheus metrics for the FastAPI application.
