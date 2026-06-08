#!/usr/bin/env bash
# Convenience setup for a Linux GPU evaluation host.

set -euo pipefail

echo "=========================================================="
echo " Vision GPU Node Setup"
echo "=========================================================="

if [[ ! -f .env ]]; then
    cp .env.example .env
    echo "Created .env from .env.example"
fi

MODEL_ROOT=$(awk -F= '/^MODEL_ROOT=/{print $2}' .env | tail -n 1)
MODEL_ROOT=${MODEL_ROOT:-./models}
MODEL_ROOT=${MODEL_ROOT%\"}
MODEL_ROOT=${MODEL_ROOT#\"}
MODEL_ROOT=${MODEL_ROOT%\'}
MODEL_ROOT=${MODEL_ROOT#\'}
MODEL_ROOT=$(realpath -m "$MODEL_ROOT")

echo "Model root: $MODEL_ROOT"

required_dirs=(
    "$MODEL_ROOT/Qwen2.5-VL-7B-Instruct"
    "$MODEL_ROOT/Qwen2.5-VL-32B-Instruct-AWQ"
    "$MODEL_ROOT/bge-m3"
    "$MODEL_ROOT/bge-reranker-v2-m3"
)

missing=0
for dir in "${required_dirs[@]}"; do
    if [[ ! -d "$dir" ]]; then
        echo "Missing model directory: $dir"
        missing=1
    fi
done

if [[ "$missing" -eq 1 ]]; then
    echo ""
    echo "The supplied model bundle was not found in the expected layout."
    echo "Place it at $MODEL_ROOT, or set MODEL_ROOT in .env."
    echo ""
    read -r -p "Download models into this folder now? This requires internet access. [y/N] " reply
    if [[ "$reply" =~ ^[Yy]$ ]]; then
        MODEL_ROOT="$MODEL_ROOT" bash scripts/download-models.sh
    else
        echo "Setup stopped before download. Fix MODEL_ROOT/model placement and rerun."
        exit 1
    fi
fi

bash scripts/validate-deployment.sh

echo ""
echo "Setup complete."
echo "Start the stack with: docker compose up -d"
