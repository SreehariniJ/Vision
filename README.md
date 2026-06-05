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

Follow these instructions to deploy the system on the VSSC RHEL 9 VM with NVIDIA A40 GPUs.

### 1. Clone the Repository
Pull the code directly from Git onto your GPU server:
```bash
git clone https://github.com/SreehariniJ/Vision.git
cd Vision
```

### 2. Environment Configuration
Copy the sample environment file.
```bash
cp .env.example .env
```
Open `.env` and fill in any required passwords. 

**IMPORTANT**: If your guide has **already downloaded** the required HuggingFace models to a specific folder on the server (e.g. `/mnt/data/vssc-models`), edit the `.env` file and set the `HF_HOME_HOST` variable to that path:
```env
HF_HOME_HOST=/mnt/data/vssc-models
```
*(If you are downloading the models yourself, leave this as the default `~/.cache/huggingface`)*

### 3. Model Preparation
The system relies on huge LLM and embedding models which can be slow to download via Docker. Run the provided setup script. It will automatically detect if models exist, and if not, it will install a high-speed downloader to fetch them.
```bash
chmod +x setup_gpu_node.sh
./setup_gpu_node.sh
```

### 4. Boot the System
Once the setup script finishes (or skips if it found existing models), boot the entire stack:
```bash
docker compose up -d
```

### 5. Access the Interface
The ChatGPT-style frontend will be available at port 3002.
- **UI:** `http://<YOUR_GPU_IP>:3002`
- **Backend API:** `http://<YOUR_GPU_IP>:8000/docs`

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
