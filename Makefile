# ============================================================
# Vision - Deployment and Operations
# ============================================================

.PHONY: help setup validate up down build logs logs-vllm logs-backend \
        switch-model dev dev-down dev-build dev-logs test lint clean status \
        health download-models

PROFILE ?= A
COMPOSE_GPU = docker compose
COMPOSE_DEV = docker compose -f docker-compose.yml -f docker-compose.dev.yml

help: ## Show this help
	@echo ""
	@echo "  Vision - Multi-Modal RAG System"
	@echo "  ================================"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'
	@echo ""

# --- Evaluation / production (GPU) ---

setup: ## Create .env if needed and run deployment preflight
	bash setup_gpu_node.sh

validate: ## Run deployment preflight checks
	bash scripts/validate-deployment.sh

up: validate ## Start full stack (GPU required)
	$(COMPOSE_GPU) up -d --build
	@echo ""
	@echo "Vision is starting."
	@echo "UI:      http://localhost:$${OPENWEBUI_PORT:-3000}"
	@echo "API:     http://localhost:$${BACKEND_PORT:-8000}/api/health"
	@echo "Grafana: http://localhost:$${GRAFANA_PORT:-3001}"

down: ## Stop all services
	$(COMPOSE_GPU) down

build: ## Build custom images
	$(COMPOSE_GPU) build

logs: ## Tail logs for all services
	$(COMPOSE_GPU) logs -f

logs-vllm: ## Tail vLLM logs
	$(COMPOSE_GPU) logs -f vllm

logs-backend: ## Tail backend logs
	$(COMPOSE_GPU) logs -f backend

status: ## Show service status
	$(COMPOSE_GPU) ps

health: ## Check backend health endpoint
	@curl -fsS http://localhost:$${BACKEND_PORT:-8000}/api/health
	@echo ""

download-models: ## Download all required model weights into MODEL_ROOT
	bash scripts/download-models.sh

# --- Development (no GPU) ---

dev: ## Start dev stack with mock LLM
	$(COMPOSE_DEV) up -d
	@echo "Vision dev stack is starting at http://localhost:$${OPENWEBUI_PORT:-3000}"

dev-down: ## Stop dev stack
	$(COMPOSE_DEV) down

dev-build: ## Build dev images
	$(COMPOSE_DEV) build

dev-logs: ## Tail dev logs
	$(COMPOSE_DEV) logs -f

# --- Testing ---

test: ## Run backend tests
	cd backend && python -m pytest tests/ -v

lint: ## Run backend linters
	cd backend && ruff check app/
	cd backend && mypy app/

# --- Maintenance ---

clean: ## Remove all data volumes (destructive)
	@echo "This will delete all Docker data volumes for the Vision stack."
	@read -p "Are you sure? [y/N] " confirm && [ "$$confirm" = "y" ] || exit 1
	$(COMPOSE_GPU) down -v
