# Vision - Multi-Modal RAG System

Vision is a containerized multi-modal RAG system with OpenWebUI, FastAPI orchestration, vLLM, BGE-M3 embeddings, BGE reranking, Docling, PaddleOCR, MySQL, Qdrant, Neo4j, Redis, MinIO, Prometheus, and Grafana.

The production deployment path is designed for RHEL/Fedora-family GPU hosts: Red Hat Enterprise Linux, Rocky Linux, AlmaLinux, and Fedora.

## Fast Evaluation Path

Prerequisites on the Linux GPU host:

- Docker Engine with Docker Compose V2
- NVIDIA driver working with `nvidia-smi`
- NVIDIA Container Toolkit configured for Docker
- A GPU with enough VRAM for the selected profile
- Internet access for image pulls/build-time Python dependencies, unless images are prebuilt

Place the supplied model bundle in this layout:

```text
vision/
  models/
    Qwen2.5-VL-7B-Instruct/
    Qwen2.5-VL-32B-Instruct-AWQ/
    bge-m3/
    bge-reranker-v2-m3/
```

If the model folder is outside the project, set `MODEL_ROOT=/absolute/path/to/models` in `.env`.

Run:

```bash
cd vision
cp .env.example .env
bash scripts/validate-deployment.sh
make up
```

Open:

- UI: `http://<host>:3000`
- Backend health: `http://<host>:8000/api/health`
- Backend readiness: `http://<host>:8000/api/ready`
- Grafana: `http://<host>:3001`

The first OpenWebUI user to register becomes the admin user.

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
