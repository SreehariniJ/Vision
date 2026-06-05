#!/bin/bash
# ============================================================
# Vision — Switch Model Profile
# ============================================================

set -e

if [ -z "$1" ]; then
    echo "Usage: ./switch-model.sh [A|B]"
    echo ""
    echo "Profiles:"
    echo "  A : Qwen2.5-VL-7B-Instruct (Unquantized)"
    echo "  B : Qwen2.5-VL-32B-Instruct-AWQ (4-bit Quantized)"
    exit 1
fi

PROFILE=$(echo "$1" | tr '[:upper:]' '[:lower:]')
PROFILE_FILE=".env.profiles/config-${PROFILE}.env"

if [ ! -f "$PROFILE_FILE" ]; then
    echo "❌ Error: Profile file $PROFILE_FILE does not exist."
    exit 1
fi

echo "🔄 Switching to model profile: $1"

# Copy the profile to the active env file
cp "$PROFILE_FILE" .env.active-model

# Restart the vLLM container
echo "⏳ Restarting vLLM container..."
docker compose up -d vllm

echo "✅ Successfully switched to profile $1."
echo "You can monitor the loading process with: make logs-vllm"
