# Deployment Guide

This guide covers deploying the Vision RAG system on a RHEL 9 virtual machine equipped with an NVIDIA A40 (48GB VRAM) GPU.

## Prerequisites

1. **RHEL 9 Server** with internet access (for initial model download).
2. **NVIDIA Driver** installed and verified via `nvidia-smi`.
3. **Docker Engine & Docker Compose V2** (or Podman with `podman-compose`).
   * *Note: If using Podman, ensure GPU passthrough is configured correctly using the `cdi` feature.*
4. **NVIDIA Container Toolkit** installed to allow containers to access the GPU.
5. **Git** and **Make**.

## Step 1: System Preparation

Clone the repository to the VM:
```bash
git clone <repository-url> vision
cd vision
```

Copy the environment template:
```bash
cp .env.example .env
```
**CRITICAL:** Edit `.env` and replace all `change-me` values with strong, secure passwords before proceeding.

## Step 2: Download Models

The system requires several large AI models. Download them to the local HuggingFace cache:
```bash
make download-models
```
*This step requires ~40GB of disk space and a stable internet connection.*

## Step 3: Start the System

Bring up the full stack using Docker Compose:
```bash
make up
```

This command will:
1. Build the custom images (FastAPI, Docling, OCR, Embedding, Reranker).
2. Initialize the databases (MySQL schemas, Neo4j constraints).
3. Start the vLLM server with **Config A (Qwen2.5-VL-7B-Instruct)** by default.

## Step 4: Verify Deployment

Check that all containers are running:
```bash
make status
```

Check the vLLM logs to ensure the model loaded successfully onto the GPU:
```bash
make logs-vllm
```
*Look for "Application startup complete." and note the GPU memory allocation.*

## Step 5: Initial Configuration

1. Navigate to `http://<vm-ip>:3000` (OpenWebUI).
2. The first user to register automatically becomes the **Admin**.
3. Create your account.
4. Go to **Settings > Connections** and verify that the OpenAI API Base URL is pointing to the backend (e.g., `http://backend:8000/v1`).
5. Ensure the API Key matches the `OPENAI_API_KEY` set in your `.env` file.

## Switching Models

To demonstrate the higher-quality quantized model:
```bash
make switch-model PROFILE=B
```
This stops the current vLLM container, updates the environment variables, and restarts vLLM with `Qwen2.5-VL-32B-Instruct-AWQ`. The frontend will automatically detect the new model once it finishes loading.

## Monitoring

Access the Grafana dashboard to monitor system health:
1. Navigate to `http://<vm-ip>/grafana/` (or port 3001 if bypassing Nginx).
2. Login with credentials set in `.env` (`GRAFANA_ADMIN_USER` / `GRAFANA_ADMIN_PASSWORD`).
3. View the "Vision System Health" dashboard.
