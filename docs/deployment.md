# Deployment Guide

This guide is for final evaluation on RHEL/Fedora-family Linux GPU systems, including RHEL, Rocky Linux, AlmaLinux, and Fedora.

## Required Host Software

Verify the host before launching:

```bash
cat /etc/os-release
nvidia-smi
docker --version
docker compose version
docker info
```

The deployment expects:

- NVIDIA driver installed and visible through `nvidia-smi`
- Docker Engine running
- Docker Compose V2
- NVIDIA Container Toolkit configured for Docker GPU access
- Enough free disk space for Docker images, volumes, and the supplied models

## Model Folder

Default expected layout:

```text
vision/
  models/
    Qwen2.5-VL-7B-Instruct/
    Qwen2.5-VL-32B-Instruct-AWQ/
    bge-m3/
    bge-reranker-v2-m3/
```

If the evaluator receives models as a separate folder, either copy that folder into the project as `vision/models` or set an absolute path in `.env`:

```bash
MODEL_ROOT=/path/to/models
```

The containers mount this folder read-only at `/models`.

## First Launch

```bash
cd vision
cp .env.example .env
bash scripts/validate-deployment.sh
make up
```

`make up` runs preflight validation and starts the stack with `docker compose up -d --build`.

If build-time downloads are not allowed on the evaluation machine, prebuild and transfer the Docker images before evaluation. The project folder plus model folder alone is enough for configuration, but Docker image pulls and Python package installation still require either internet access or preloaded images/caches.

## Readiness Checks

Container status:

```bash
docker compose ps
```

Backend liveness:

```bash
curl -fsS http://localhost:8000/api/health
```

Dependency readiness:

```bash
curl -fsS http://localhost:8000/api/ready
```

Model server logs:

```bash
docker compose logs -f vllm
```

Look for vLLM startup completion and absence of model path errors.

## Access URLs

- OpenWebUI: `http://<host>:3000`
- Backend API docs: `http://<host>:8000/docs`
- Backend readiness: `http://<host>:8000/api/ready`
- Grafana: `http://<host>:3001`
- MinIO console: `http://<host>:9001`

## Switching Models

The default active profile is A.

```bash
make switch-model PROFILE=A
make switch-model PROFILE=B
```

The switch script validates that the selected packaged model directory exists, updates `.env.active-model`, and force-recreates the vLLM container.

## Optional Smoke Test

After all services are healthy:

```bash
python3 test_e2e.py
```

This uploads `test_documents/2_Simple_Text.pdf`, waits for ingestion to reach `indexed`, and runs a search query.

## Troubleshooting

Missing model folder:

```bash
bash scripts/validate-deployment.sh
```

Use the reported `MODEL_ROOT` and missing directory paths to fix placement.

GPU not visible inside containers:

```bash
nvidia-smi
docker info | grep -i nvidia
docker compose logs embedding reranker vllm
```

SELinux bind mount issues:

- The Compose file uses `:z` labels for host bind mounts.
- If a custom `MODEL_ROOT` is used, keep it readable by the Docker daemon.

Port conflicts:

- The preflight reports common port conflicts.
- Change the corresponding port variable in `.env` if needed.

Slow first launch:

- vLLM model loading can take several minutes.
- Docling and PaddleOCR are pre-initialized during image build to avoid first-request surprises.
