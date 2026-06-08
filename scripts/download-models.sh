#!/usr/bin/env bash
# Download required models into the local deployment model folder.

set -euo pipefail

MODEL_ROOT=${MODEL_ROOT:-./models}
MODEL_ROOT=$(realpath -m "$MODEL_ROOT")

echo "========================================"
echo " Vision - Model Downloader"
echo "========================================"
echo "Destination: $MODEL_ROOT"
echo "Required free space: roughly 60 GB"
echo ""

if ! command -v python3 >/dev/null 2>&1; then
    echo "ERROR: python3 is required to install/run huggingface-cli." >&2
    exit 1
fi

if ! command -v huggingface-cli >/dev/null 2>&1; then
    echo "Installing Hugging Face CLI..."
    python3 -m pip install -U "huggingface_hub[cli]" hf_transfer
fi

export HF_HUB_ENABLE_HF_TRANSFER=${HF_HUB_ENABLE_HF_TRANSFER:-1}
mkdir -p "$MODEL_ROOT"

download_model() {
    local repo_id="$1"
    local target_dir="$2"

    echo "Downloading $repo_id"
    echo "  -> $target_dir"
    mkdir -p "$target_dir"
    huggingface-cli download "$repo_id" --local-dir "$target_dir"
}

download_model "Qwen/Qwen2.5-VL-7B-Instruct" "$MODEL_ROOT/Qwen2.5-VL-7B-Instruct"
download_model "Qwen/Qwen2.5-VL-32B-Instruct-AWQ" "$MODEL_ROOT/Qwen2.5-VL-32B-Instruct-AWQ"
download_model "BAAI/bge-m3" "$MODEL_ROOT/bge-m3"
download_model "BAAI/bge-reranker-v2-m3" "$MODEL_ROOT/bge-reranker-v2-m3"

echo ""
echo "All required models are present under: $MODEL_ROOT"
echo "Run the preflight next: bash scripts/validate-deployment.sh"
