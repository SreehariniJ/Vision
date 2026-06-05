#!/bin/bash
set -e

echo "=========================================================="
echo " Vision GPU Node Setup Script"
echo "=========================================================="

# Check if the user already has models downloaded
if [ -z "$HF_HOME_HOST" ]; then
    HF_HOME_HOST="$HOME/.cache/huggingface"
fi

echo "Checking for existing Hugging Face cache at: $HF_HOME_HOST"

if [ -d "$HF_HOME_HOST/hub" ] && [ "$(ls -A $HF_HOME_HOST/hub 2>/dev/null)" ]; then
    echo ""
    echo "✅ SUCCESS: Existing models found in $HF_HOME_HOST/hub!"
    echo "If your guide already downloaded the models here, you DO NOT need to download them again."
    echo "The system will use these models automatically."
    echo ""
    read -p "Do you want to run the downloader anyway to ensure all required models are present? (y/N) " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Setup complete! You can now run: docker compose up -d"
        exit 0
    fi
else
    echo "No existing cache found. Proceeding with download..."
fi

echo ""
echo "Setting up high-speed downloader (hf_transfer)..."
# Check for python/pip
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 not found. Please install python3-pip first."
    exit 1
fi

pip3 install -U "huggingface_hub[cli]" hf_transfer

# Enable blazing fast rust-based downloads
export HF_HUB_ENABLE_HF_TRANSFER=1
export HF_HOME="$HF_HOME_HOST"

echo ""
echo "Downloading Qwen2.5-VL-7B-Instruct (LLM)..."
huggingface-cli download Qwen/Qwen2.5-VL-7B-Instruct

echo ""
echo "Downloading BAAI/bge-m3 (Embedding)..."
huggingface-cli download BAAI/bge-m3

echo ""
echo "Downloading BAAI/bge-reranker-v2-m3 (Reranker)..."
huggingface-cli download BAAI/bge-reranker-v2-m3

echo ""
echo "=========================================================="
echo "✅ Setup Complete!"
echo "All models are cached in: $HF_HOME_HOST"
echo ""
echo "You can now boot the system:"
echo "docker compose up -d"
echo "=========================================================="
