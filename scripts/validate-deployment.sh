#!/usr/bin/env bash
# Preflight checks for RHEL/Fedora-family GPU deployment.

set -uo pipefail

FAILURES=0
WARNINGS=0

pass() { printf 'PASS: %s\n' "$1"; }
warn() { printf 'WARN: %s\n' "$1"; WARNINGS=$((WARNINGS + 1)); }
fail() { printf 'FAIL: %s\n' "$1"; FAILURES=$((FAILURES + 1)); }

read_env() {
    local key="$1"
    local file="${2:-.env}"
    [[ -f "$file" ]] || return 0
    awk -F= -v key="$key" '$1 == key {print substr($0, length(key) + 2)}' "$file" | tail -n 1
}

strip_quotes() {
    local value="$1"
    value="${value%\"}"
    value="${value#\"}"
    value="${value%\'}"
    value="${value#\'}"
    printf '%s' "$value"
}

resolve_model_root() {
    local configured
    configured=$(strip_quotes "$(read_env MODEL_ROOT)")
    configured=${configured:-./models}
    realpath -m "$configured" 2>/dev/null || printf '%s\n' "$configured"
}

check_command() {
    local command_name="$1"
    local message="$2"
    if command -v "$command_name" >/dev/null 2>&1; then
        pass "$message"
    else
        fail "$command_name is not installed or is not on PATH."
    fi
}

check_file() {
    local path="$1"
    local message="$2"
    if [[ -f "$path" ]]; then
        pass "$message"
    else
        fail "Missing file: $path"
    fi
}

check_dir() {
    local path="$1"
    local message="$2"
    if [[ -d "$path" ]]; then
        pass "$message"
    else
        fail "Missing directory: $path"
    fi
}

check_model_dir() {
    local path="$1"
    local label="$2"

    if [[ ! -d "$path" ]]; then
        fail "$label model directory is missing: $path"
        return
    fi

    local missing=0
    for required_file in config.json tokenizer_config.json; do
        if [[ ! -f "$path/$required_file" ]]; then
            printf 'FAIL: %s is missing %s\n' "$label" "$required_file"
            missing=1
        fi
    done

    if ! find "$path" -maxdepth 2 -type f \( -name '*.safetensors' -o -name '*.bin' \) -print -quit | grep -q .; then
        printf 'FAIL: %s has no model weight files (*.safetensors or *.bin)\n' "$label"
        missing=1
    fi

    if [[ "$missing" -eq 0 ]]; then
        pass "$label model files found"
    else
        FAILURES=$((FAILURES + 1))
    fi
}

echo "=========================================================="
echo " Vision Deployment Preflight"
echo "=========================================================="

if [[ "$(uname -s)" != "Linux" ]]; then
    fail "Target deployment must run on Linux. Current OS: $(uname -s)"
else
    pass "Linux host detected"
fi

if [[ -f /etc/os-release ]]; then
    # shellcheck disable=SC1091
    . /etc/os-release
    distro_id=${ID:-unknown}
    distro_like=${ID_LIKE:-}
    case " $distro_id $distro_like " in
        *" rhel "*|*" fedora "*|*" centos "*|*" rocky "*|*" almalinux "*)
            pass "RHEL/Fedora-family distribution detected: ${PRETTY_NAME:-$distro_id}"
            ;;
        *)
            warn "Distribution is not RHEL/Fedora-family: ${PRETTY_NAME:-$distro_id}"
            ;;
    esac
else
    warn "/etc/os-release not found; cannot verify distribution family."
fi

if [[ -f .env ]]; then
    pass ".env exists"
else
    fail ".env is missing. Run: cp .env.example .env"
fi

check_file ".env.active-model" ".env.active-model exists"
check_file "docker-compose.yml" "docker-compose.yml exists"
check_file "scripts/init-db.sql" "MySQL initialization script exists"

check_command docker "Docker CLI is available"
if command -v docker >/dev/null 2>&1; then
    if docker compose version >/dev/null 2>&1; then
        pass "Docker Compose V2 is available"
    else
        fail "Docker Compose V2 is unavailable. Install the Docker Compose plugin."
    fi

    if docker info >/dev/null 2>&1; then
        pass "Docker daemon is reachable"
    else
        fail "Docker daemon is not reachable by this user."
    fi

    if docker info --format '{{json .Runtimes}}' 2>/dev/null | grep -qi nvidia; then
        pass "NVIDIA container runtime is registered with Docker"
    else
        warn "NVIDIA runtime was not listed by docker info. Verify NVIDIA Container Toolkit before GPU launch."
    fi
fi

if command -v nvidia-smi >/dev/null 2>&1; then
    if nvidia-smi >/dev/null 2>&1; then
        pass "nvidia-smi can access the GPU"
        gpu_summary=$(nvidia-smi --query-gpu=name,memory.total --format=csv,noheader 2>/dev/null | head -n 1)
        [[ -n "$gpu_summary" ]] && printf 'INFO: GPU: %s\n' "$gpu_summary"
    else
        fail "nvidia-smi exists but cannot access the GPU."
    fi
else
    fail "nvidia-smi is missing. Install/verify the NVIDIA driver."
fi

if command -v getenforce >/dev/null 2>&1; then
    selinux_state=$(getenforce 2>/dev/null || true)
    if [[ "$selinux_state" == "Enforcing" ]]; then
        pass "SELinux is enforcing; compose bind mounts include :z labels"
    else
        pass "SELinux state: ${selinux_state:-unknown}"
    fi
fi

model_root=$(resolve_model_root)
printf 'INFO: MODEL_ROOT=%s\n' "$model_root"
check_dir "$model_root" "Model root exists"
check_model_dir "$model_root/Qwen2.5-VL-7B-Instruct" "Qwen2.5-VL-7B-Instruct"
check_model_dir "$model_root/Qwen2.5-VL-32B-Instruct-AWQ" "Qwen2.5-VL-32B-Instruct-AWQ"
check_model_dir "$model_root/bge-m3" "bge-m3"
check_model_dir "$model_root/bge-reranker-v2-m3" "bge-reranker-v2-m3"

active_model=$(strip_quotes "$(read_env VLLM_MODEL .env.active-model)")
case "$active_model" in
    /models/Qwen2.5-VL-7B-Instruct|/models/Qwen2.5-VL-32B-Instruct-AWQ)
        pass "Active vLLM model path is deployment-local: $active_model"
        ;;
    "")
        fail "VLLM_MODEL is not set in .env.active-model."
        ;;
    *)
        warn "Active vLLM model is not one of the packaged local paths: $active_model"
        ;;
esac

for port_key in OPENWEBUI_PORT BACKEND_PORT VLLM_PORT EMBEDDING_PORT RERANKER_PORT DOCLING_PORT OCR_PORT MYSQL_PORT QDRANT_PORT NEO4J_HTTP_PORT NEO4J_BOLT_PORT REDIS_PORT MINIO_PORT MINIO_CONSOLE_PORT PROMETHEUS_PORT GRAFANA_PORT; do
    port_value=$(strip_quotes "$(read_env "$port_key")")
    [[ -n "$port_value" ]] || continue
    if command -v ss >/dev/null 2>&1 && ss -ltn "( sport = :$port_value )" 2>/dev/null | grep -q ":$port_value"; then
        warn "Port $port_value ($port_key) is already listening. Stop the conflicting service or change .env."
    fi
done

if command -v docker >/dev/null 2>&1 && docker compose version >/dev/null 2>&1; then
    if docker compose config -q >/dev/null 2>&1; then
        pass "Docker Compose configuration is valid"
    else
        fail "Docker Compose configuration is invalid. Run: docker compose config"
    fi
fi

echo "=========================================================="
if [[ "$FAILURES" -gt 0 ]]; then
    echo "Preflight failed with $FAILURES failure(s) and $WARNINGS warning(s)."
    exit 1
fi

echo "Preflight passed with $WARNINGS warning(s)."
echo "Next step: docker compose up -d"
