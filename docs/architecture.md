# System Architecture

The Vision RAG system is designed as a microservices architecture orchestrated via Docker Compose, optimized for a single NVIDIA A40 (48GB) GPU.

## High-Level Architecture

The system uses an "Always-On Auxiliary, Swap-on-Demand LLM" strategy. The core infrastructure (databases, embedding models, OCR) remains active, while the primary Large Language Model (LLM) can be swapped between profiles depending on the required task complexity.

### Component Overview

1. **Client Interface (OpenWebUI)**
   * Provides the user-facing chat interface, document upload capabilities, and authentication flow.

2. **API Gateway (FastAPI)**
   * Acts as the central orchestrator.
   * Handles the RAG pipeline logic: query formulation, hybrid search execution, context merging, and prompt construction.
   * Exposes an OpenAI-compatible API to the frontend.

3. **Asynchronous Processing (Celery & Redis)**
   * Heavy tasks like document parsing (Docling), OCR (PaddleOCR), chunking, and embedding are offloaded to Celery workers to keep the API responsive.

4. **Model Serving (vLLM)**
   * Serves the primary text/vision generative models.
   * Leverages PagedAttention for high-throughput generation.

5. **Data Stores**
   * **MinIO**: Stores raw uploaded documents and images.
   * **MySQL**: Relational metadata (users, document status, audit logs).
   * **Qdrant**: Vector database for dense semantic similarity search.
   * **Neo4j**: Knowledge graph database for structured relationship traversal.

## Data Flows

### Ingestion Pipeline
When a user uploads a document:
1. File saved to MinIO; record created in MySQL.
2. Celery task triggered.
3. Docling parses layout; PaddleOCR extracts text from images/scans.
4. Text is chunked and embedded via the BGE-M3 service.
5. Embeddings are stored in Qdrant; extracted entities/relationships are mapped into Neo4j.

### Retrieval Pipeline (RAG)
When a user asks a question:
1. The API checks if an image is attached. If so, it routes it appropriately based on the active model's vision capabilities.
2. The user's query is embedded.
3. **Hybrid Search** executes in parallel:
   * Qdrant retrieves the top-K semantically similar chunks.
   * Neo4j retrieves structurally related nodes (entities/topics).
4. Results are merged, deduplicated, and passed to the **BGE-Reranker** service to refine the top results.
5. The reranked context is injected into the system prompt and sent to vLLM.
6. The response is streamed back to the user via SSE.
