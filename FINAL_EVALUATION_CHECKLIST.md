# Final Evaluation Checklist

Pre-submission verification for the Vision Multi-Modal RAG System.

---

## 1. Project Folder Contents

Verify the evaluator deliverable contains all of these:

| Item | Check |
|------|-------|
| `docker-compose.yml` | ☐ |
| `.env.example` | ☐ |
| `.env.active-model` (defaults to Profile A) | ☐ |
| `.env.profiles/config-a.env` | ☐ |
| `.env.profiles/config-b.env` | ☐ |
| `.gitattributes` (forces LF line endings) | ☐ |
| `Makefile` | ☐ |
| `backend/Dockerfile` + `requirements.txt` + `app/` | ☐ |
| `services/embedding/Dockerfile` + `app.py` + `requirements.txt` | ☐ |
| `services/reranker/Dockerfile` + `app.py` + `requirements.txt` | ☐ |
| `services/docling/Dockerfile` + `app.py` + `requirements.txt` | ☐ |
| `services/ocr/Dockerfile` + `app.py` + `requirements.txt` | ☐ |
| `scripts/validate-deployment.sh` | ☐ |
| `scripts/switch-model.sh` | ☐ |
| `scripts/download-models.sh` | ☐ |
| `scripts/init-db.sql` | ☐ |
| `scripts/init-neo4j.cypher` | ☐ |
| `setup_gpu_node.sh` | ☐ |
| `nginx/nginx.conf` + `nginx/conf.d/default.conf` | ☐ |
| `nginx/ssl/.gitkeep` (empty dir placeholder) | ☐ |
| `monitoring/prometheus/prometheus.yml` | ☐ |
| `monitoring/grafana/provisioning/` | ☐ |
| `test_documents/` (3 test files) | ☐ |
| `test_e2e.py` | ☐ |
| `docs/deployment.md` + `architecture.md` + `api-reference.md` | ☐ |
| `README.md` | ☐ |

**The project folder must NOT contain**: `.env` (evaluator creates it from `.env.example`), `models/` (supplied separately).

---

## 2. Model Folder Contents

The separate models folder must contain exactly this layout:

```text
models/
├── Qwen2.5-VL-7B-Instruct/
│   ├── config.json
│   ├── tokenizer_config.json
│   └── *.safetensors (or *.bin)
├── Qwen2.5-VL-32B-Instruct-AWQ/
│   ├── config.json
│   ├── tokenizer_config.json
│   └── *.safetensors (or *.bin)
├── bge-m3/
│   ├── config.json
│   └── *.safetensors (or *.bin)
└── bge-reranker-v2-m3/
    ├── config.json
    └── *.safetensors (or *.bin)
```

Each model directory must have `config.json` and at least one weight file.

---

## 3. Evaluation Machine Prerequisites

| Requirement | Verify With |
|-------------|-------------|
| Linux OS | `uname -s` → `Linux` |
| NVIDIA driver | `nvidia-smi` shows GPU |
| Docker Engine running | `docker info` |
| Docker Compose V2 | `docker compose version` |
| NVIDIA Container Toolkit | `docker info \| grep -i nvidia` |
| Sufficient VRAM (≥24GB for Profile A, ≥48GB for Profile B) | `nvidia-smi` |
| Free disk space (≥50GB for images + volumes) | `df -h` |
| Internet access (for Docker image pulls and pip installs during build) | `curl -I https://pypi.org` |

---

## 4. Evaluator Startup Sequence

```bash
# 1. Copy project and models to the machine
cp -r /source/vision ~/vision
cp -r /source/models ~/vision/models
# (Or set MODEL_ROOT=/path/to/models in .env after step 2)

# 2. Create environment config
cd ~/vision
cp .env.example .env

# 3. Run preflight validation
bash scripts/validate-deployment.sh

# 4. Start the full stack
make up

# 5. Wait for all services (2-10 minutes depending on GPU)
docker compose ps
# Watch vLLM startup specifically:
docker compose logs -f vllm

# 6. Verify readiness
curl -fsS http://localhost:8000/api/health
curl -fsS http://localhost:8000/api/ready
```

---

## 5. Post-Launch Verification

| Check | Command | Expected |
|-------|---------|----------|
| All containers running | `docker compose ps` | All `Up (healthy)` |
| Backend liveness | `curl localhost:8000/api/health` | `{"status":"ok"}` |
| Backend readiness | `curl localhost:8000/api/ready` | All checks `"status":"ok"` |
| vLLM model loaded | `curl localhost:8001/health` | `{"status":"ok"}` |
| Embedding service | `curl localhost:8003/health` | `{"status":"ok"}` |
| Reranker service | `curl localhost:8004/health` | `{"status":"ok"}` |
| OpenWebUI accessible | Browser → `http://<host>:3000` | Registration page |

---

## 6. Model Profile Switch

Default is Profile A (7B). To switch to Profile B (32B AWQ):

```bash
make switch-model PROFILE=B
docker compose logs -f vllm  # Wait for model load
```

---

## 7. Known Considerations

- **First launch is slow**: Docker builds, Python package installation, and model loading take time.
- **vLLM startup**: Takes 2-5 minutes to load weights into GPU memory.
- **OpenWebUI first user**: The first user to register becomes the admin.
- **Offline mode**: `HF_HUB_OFFLINE=1` and `TRANSFORMERS_OFFLINE=1` prevent runtime downloads. Models must be pre-placed.
- **Internet required at build time**: Docker image pulls and `pip install` need network access unless images are prebuilt.
