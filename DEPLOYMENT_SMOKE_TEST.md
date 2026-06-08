# Deployment Smoke Test

Run these tests after `docker compose ps` shows all services as `Up (healthy)`.

---

## Quick Health Checks

```bash
# Backend liveness (should return immediately)
curl -fsS http://localhost:8000/api/health
# Expected: {"status":"ok","project":"Vision"}

# Full dependency readiness (checks all 10 backends)
curl -fsS http://localhost:8000/api/ready | python3 -m json.tool
# Expected: all checks show "status":"ok"
```

If `/api/ready` reports any check as `"error"`, see which service failed and check its logs:

```bash
docker compose logs <service-name>
```

---

## Service-Level Checks

```bash
# vLLM model server
curl -fsS http://localhost:8001/health
curl -fsS http://localhost:8001/v1/models | python3 -m json.tool

# Embedding service
curl -fsS http://localhost:8003/health

# Reranker service
curl -fsS http://localhost:8004/health

# Docling document parser
curl -fsS http://localhost:8005/health

# OCR service
curl -fsS http://localhost:8006/health
```

---

## Functional Smoke Test

### 1. Embedding Test

```bash
curl -s -X POST http://localhost:8003/v1/embeddings \
  -H "Content-Type: application/json" \
  -d '{"input": "Hello world", "model": "bge-m3"}' | python3 -m json.tool
# Expected: JSON with "data" containing an embedding array
```

### 2. Reranker Test

```bash
curl -s -X POST http://localhost:8004/rerank \
  -H "Content-Type: application/json" \
  -d '{"query": "What is machine learning?", "documents": ["ML is a subset of AI", "The weather is sunny", "Deep learning uses neural networks"], "top_k": 2}' | python3 -m json.tool
# Expected: JSON with "results" sorted by relevance score
```

### 3. LLM Inference Test

```bash
curl -s -X POST http://localhost:8001/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model": "vision-model", "messages": [{"role": "user", "content": "Say hello in one sentence."}], "max_tokens": 50}' | python3 -m json.tool
# Expected: JSON with assistant response
```

### 4. End-to-End Pipeline Test (Optional)

Requires `requests` Python package on the host:

```bash
pip3 install requests  # if not already installed
python3 test_e2e.py
```

This uploads `test_documents/2_Simple_Text.pdf`, waits for ingestion to complete, and runs a search query.

---

## OpenWebUI Access

1. Open `http://<host>:3000` in a browser
2. Register a new user (first user becomes admin)
3. Send a chat message to verify end-to-end inference
4. Upload a document through the UI to verify ingestion

---

## Troubleshooting Quick Reference

| Symptom | Check |
|---------|-------|
| vLLM won't start | `docker compose logs vllm` — look for model path or CUDA errors |
| Embedding/Reranker crash | `docker compose logs embedding reranker` — check model path and CUDA |
| Backend unhealthy | `docker compose logs backend` — check database connectivity |
| "VLLM_MODEL is not set" | Run `bash scripts/switch-model.sh A` to reset the active profile |
| Port already in use | Change the port in `.env` or stop the conflicting service |
| Permission denied on volumes | Check SELinux: `getenforce` — compose uses `:z` labels for bind mounts |
| Model not found inside container | Verify `MODEL_ROOT` in `.env` points to the correct host path |
