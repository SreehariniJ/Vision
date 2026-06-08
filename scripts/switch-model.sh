#!/usr/bin/env bash
# Switch the active vLLM model profile.

set -euo pipefail

usage() {
    cat <<'EOF'
Usage: bash scripts/switch-model.sh A|B

Profiles:
  A  Qwen2.5-VL-7B-Instruct
  B  Qwen2.5-VL-32B-Instruct-AWQ
EOF
}

if [[ $# -ne 1 ]]; then
    usage
    exit 1
fi

profile_upper=$(printf '%s' "$1" | tr '[:lower:]' '[:upper:]')
profile_lower=$(printf '%s' "$profile_upper" | tr '[:upper:]' '[:lower:]')

case "$profile_upper" in
    A|B) ;;
    *)
        usage
        exit 1
        ;;
esac

profile_file=".env.profiles/config-${profile_lower}.env"
active_file=".env.active-model"

if [[ ! -f "$profile_file" ]]; then
    echo "ERROR: Profile file not found: $profile_file" >&2
    exit 1
fi

cp "$profile_file" "$active_file"

selected_model=$(awk -F= '/^VLLM_MODEL=/{print $2}' "$active_file" | tail -n 1)
echo "Active profile: $profile_upper"
echo "vLLM model: ${selected_model:-unknown}"

if [[ "$selected_model" == /models/* ]]; then
    model_root=$(awk -F= '/^MODEL_ROOT=/{print $2}' .env 2>/dev/null | tail -n 1)
    model_root=${model_root:-./models}
    model_root=${model_root%\"}
    model_root=${model_root#\"}
    model_root=${model_root%\'}
    model_root=${model_root#\'}
    host_model_path="$(realpath -m "$model_root")/${selected_model#/models/}"
    if [[ ! -d "$host_model_path" ]]; then
        echo "ERROR: Selected model directory is missing on the host: $host_model_path" >&2
        echo "Fix MODEL_ROOT in .env or place the model bundle before switching." >&2
        exit 1
    fi
fi

if command -v docker >/dev/null 2>&1 && docker compose version >/dev/null 2>&1; then
    echo "Recreating vLLM with the selected profile..."
    docker compose up -d --force-recreate vllm
    echo "vLLM restart requested. Watch startup with: docker compose logs -f vllm"
else
    echo "Docker Compose was not found. Profile file updated; restart vLLM on the target host."
fi
