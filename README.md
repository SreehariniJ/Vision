# Vision - Multi-Modal RAG System

Vision is a containerized multi-modal RAG system with OpenWebUI, FastAPI orchestration, vLLM, BGE-M3 embeddings, BGE reranking, Docling, PaddleOCR, MySQL, Qdrant, Neo4j, Redis, MinIO, Prometheus, and Grafana.

The production deployment path is designed for RHEL/Fedora-family GPU hosts: Red Hat Enterprise Linux, Rocky Linux, AlmaLinux, and Fedora.

## Air-Gapped RHEL GPU Deployment Guide

This guide provides the exact workflow to deploy the Vision RAG system when you have **one internet-connected RHEL system** and **one completely offline RHEL system with a GPU**.

### Phase 1: On the INTERNET-CONNECTED RHEL System
This system will download everything and package it into a transferable format.

1. **Clone the Repository**
   ```bash
   git clone https://github.com/SreehariniJ/Vision.git
   cd Vision
   ```

2. **Download the AI Models**
   You need to download the models into the `models/` directory. You can do this manually or use the built-in downloader script:
   ```bash
   bash scripts/download-models.sh
   ```
   *Ensure that the `models/` folder contains the 4 model folders (Qwen 7B, Qwen 32B AWQ, bge-m3, and bge-reranker-v2-m3).*

3. **Package the Docker Images**
   You must build and package the microservices (like the Database, Redis, and APIs) into a single `.tar` file so they can be moved offline.
   ```bash
   bash scripts/export_offline_images_linux.sh
   ```
   *This will take 10-20 minutes. It will generate a massive file named `vision_images.tar` (approx 15 GB).*

4. **Prepare for Transfer**
   Zip or package the entire `Vision` folder (which now contains the code, the `models/` folder, and the massive `vision_images.tar` file) and move it to a USB drive or SCP it to the offline system.

### Phase 2: On the OFFLINE RHEL GPU System
This system must have **NVIDIA Drivers**, **Docker**, and the **NVIDIA Container Toolkit** installed.

1. **Unpack the Files**
   Transfer the zipped folder to this machine, unzip it, and navigate into it:
   ```bash
   cd /path/to/Vision
   ```

2. **Load the Docker Images**
   Load the packaged `.tar` file directly into Docker. Because you do this, Docker will not attempt to reach the internet.
   ```bash
   bash scripts/load_offline_images.sh
   ```

3. **Validate and Start**
   Run the setup script. It will run a pre-flight check to verify your GPU and models.
   ```bash
   make setup
   ```

   Once setup says `Preflight passed`, start the entire architecture:
   ```bash
   make up
   ```

   Wait 2 to 3 minutes for the heavy AI models to load into GPU VRAM.

4. **Access the System**
   Open a web browser and navigate to the IP address of your offline RHEL server:
   - **Chat Interface:** `http://<IP>:3000`
   - **Dashboards:** `http://<IP>:3001` (admin / change-me-grafana-password)

## Model Profiles

Vision runs one vLLM model profile at a time.

| Profile | Command | Model | Notes |
| --- | --- | --- | --- |
| A | `make switch-model PROFILE=A` | `Qwen2.5-VL-7B-Instruct` | Default, lighter startup |
| B | `make switch-model PROFILE=B` | `Qwen2.5-VL-32B-Instruct-AWQ` | Higher quality, more VRAM |

After switching, watch model startup:

```bash
docker compose logs -f vllm
```

## Validation

Run the preflight any time before launch:

```bash
bash scripts/validate-deployment.sh
```

It checks host OS family, Docker/Compose, Docker daemon access, GPU visibility, NVIDIA runtime hints, SELinux-friendly bind mounts, required model folders, active profile configuration, port conflicts, and Compose syntax.

After launch:

```bash
docker compose ps
curl -fsS http://localhost:8000/api/ready
```

## Common Operations

```bash
make status       # container status
make logs         # all logs
make logs-vllm    # model server logs
make down         # stop stack
make clean        # delete stack volumes after confirmation
```

Optional full smoke test after the stack is healthy:

```bash
python3 test_e2e.py
```

## Architecture

- OpenWebUI provides the chat interface.
- FastAPI exposes OpenAI-compatible chat endpoints and document/search APIs.
- vLLM serves Qwen2.5-VL.
- BGE-M3 and BGE-Reranker-v2-M3 provide retrieval and reranking.
- Docling and PaddleOCR handle document/image extraction.
- Celery/Redis run asynchronous ingestion.
- MySQL, Qdrant, Neo4j, and MinIO store metadata, vectors, graph data, and documents.
- Prometheus and Grafana provide operational visibility.

See [docs/deployment.md](docs/deployment.md) for the deployment checklist and [docs/architecture.md](docs/architecture.md) for system details.
