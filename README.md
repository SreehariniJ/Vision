# Vision — Multi-Modal RAG System

A production-grade, GPU-accelerated Retrieval-Augmented Generation platform built for VSSC. Features multi-modal document and image understanding, hybrid vector + knowledge-graph search, and a ChatGPT-style conversational interface.

## Quickstart (Development - No GPU)

If you are developing locally without an NVIDIA GPU, you can run the mock stack:

```bash
# 1. Copy environment variables
cp .env.example .env

# 2. Start the dev stack
make dev

# 3. Access the UI
# http://localhost:3000
```

## Getting Started (GPU Node Deployment)

### 1. Model Preparation
The system relies on huge LLM and embedding models which can be slow to download via Docker. We provide a blazing fast setup script that detects existing models or downloads them using parallel connections.

1. Clone the repository on your GPU server.
2. If your guide has **already downloaded** the models to a specific folder (e.g. `/mnt/data/models`), copy `.env.example` to `.env` and set `HF_HOME_HOST=/mnt/data/models`.
3. Run the setup script:
```bash
chmod +x setup_gpu_node.sh
./setup_gpu_node.sh
```

### 2. Boot the System
Once the setup script finishes (or skips if it found existing models), boot the entire stack:
```bash
docker compose up -d
```

### 3. Final Polish: Removing the "(Open WebUI)" Title Suffix
To ensure the application looks completely custom and professional without the Open WebUI branding in the browser tab:
1. Open the application (`http://localhost:3002`) and log in as the admin.
2. Go to **Admin Panel > Settings > General > Advanced**.
3. Paste the following into the **Custom JS** box and hit Save:
```javascript
if (document.title.includes(" (Open WebUI)")) {
    document.title = document.title.replace(" (Open WebUI)", "");
}
new MutationObserver(function(mutations) {
    if (document.title.includes(" (Open WebUI)")) {
        document.title = document.title.replace(" (Open WebUI)", "");
    }
}).observe(document.querySelector('title'), { childList: true, subtree: true });
```

## Architecture Overview

The system is composed of 16 containerized services orchestrated via Docker Compose:

- **Frontend**: OpenWebUI (ChatGPT-style interface)
- **Reverse Proxy**: Nginx
- **API Gateway**: FastAPI (RAG orchestration)
- **Model Serving**: vLLM (Qwen2.5-VL)
- **Embeddings**: BGE-M3
- **Reranker**: BGE-Reranker-v2-M3
- **Document Processing**: Docling & PaddleOCR (via Celery workers)
- **Data Stores**: MySQL, Neo4j, Qdrant, Redis, MinIO
- **Monitoring**: Prometheus & Grafana

See `docs/architecture.md` for detailed diagrams.

## Model Profiles

Vision runs **one LLM at a time** to maximize available VRAM for context caching.

| Profile | Command | Model | Type | Use Case |
|---------|---------|-------|------|----------|
| **A** | `make switch-model PROFILE=A` | `Qwen2.5-VL-7B-Instruct` | fp16 | Fast inference, good vision |
| **B** | `make switch-model PROFILE=B` | `Qwen2.5-VL-32B-Instruct-AWQ` | 4-bit | Max quality vision, deep reasoning |
