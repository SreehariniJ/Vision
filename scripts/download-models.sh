#!/bin/bash
# ============================================================
# Vision — Download Models
# Run this script once on the GPU VM to pre-download models
# ============================================================

set -e

# Default HuggingFace cache directory used by vLLM container
HF_CACHE_DIR=${HF_HOME:-~/.cache/huggingface}

echo "========================================"
echo " Vision - Model Downloader"
echo "========================================"
echo "This script will download the required models"
echo "to your local huggingface cache: $HF_CACHE_DIR"
echo "Ensure you have enough disk space (~60GB)."
echo ""

# Check for huggingface-cli
if ! command -v huggingface-cli &> /dev/null; then
    echo "huggingface-cli not found. Installing..."
    pip install -U "huggingface_hub[cli]"
fi

# 1. Config A: Qwen2.5-VL-7B-Instruct (Unquantized)
echo "[1/4] Downloading Qwen2.5-VL-7B-Instruct (~15GB)..."
huggingface-cli download Qwen/Qwen2.5-VL-7B-Instruct --cache-dir "$HF_CACHE_DIR"

# 2. Config B: Qwen2.5-VL-32B-Instruct-AWQ (Quantized)
echo "[2/4] Downloading Qwen2.5-VL-32B-Instruct-AWQ (~20GB)..."
huggingface-cli download Qwen/Qwen2.5-VL-32B-Instruct-AWQ --cache-dir "$HF_CACHE_DIR"

# 3. Embedding Model: BGE-M3
echo "[3/4] Downloading BAAI/bge-m3 (~2GB)..."
huggingface-cli download BAAI/bge-m3 --cache-dir "$HF_CACHE_DIR"

# 4. Reranker Model: BGE-Reranker-v2-M3
echo "[4/4] Downloading BAAI/bge-reranker-v2-m3 (~2GB)..."
huggingface-cli download BAAI/bge-reranker-v2-m3 --cache-dir "$HF_CACHE_DIR"

echo "========================================"
echo "✅ All models downloaded successfully!"
echo "You can now run: docker compose up -d"
echo "========================================"
