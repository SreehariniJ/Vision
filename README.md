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

## Getting Started (GPU Linux Terminal)

Follow these exact steps in your Linux terminal to download, configure, and boot the entire AI backend:

**Step 1: Clone the Project**
```bash
git clone https://github.com/SreehariniJ/Vision.git
cd Vision
```

**Step 2: Setup Configuration**
```bash
cp .env.example .env
```
*(Optional: If your guide already downloaded the massive models for you into a folder like `/mnt/models`, type `nano .env` and change `HF_HOME_HOST=~/.cache/huggingface` to `HF_HOME_HOST=/mnt/models`)*

**Step 3: Download Models**
Run the fast setup script. It automatically detects if models exist or downloads them using high-speed parallel connections.
```bash
chmod +x setup_gpu_node.sh
./setup_gpu_node.sh
```

**Step 4: Start the System**
Once the setup script is complete, boot the entire stack in the background:
```bash
docker compose up -d
```

**Step 5: Access the Web Interface**
Open your web browser and go to your server's IP address:
`http://<YOUR_LINUX_SERVER_IP>:3002`

---

### Final Polish: Removing the "(Open WebUI)" Title Suffix
To ensure the application looks completely custom and professional without the Open WebUI branding in the browser tab:
1. Open the application and log in as the admin.
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
