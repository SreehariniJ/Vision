# ============================================================
# Vision — Makefile
# ============================================================

.PHONY: help up down dev dev-down build logs switch-model clean test lint

PROFILE ?= A
COMPOSE_GPU = docker compose
COMPOSE_DEV = docker compose -f docker-compose.yml -f docker-compose.dev.yml

help: ## Show this help
	@echo ""
	@echo "  Vision — Multi-Modal RAG System"
	@echo "  ================================"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'
	@echo ""

# --- Production (GPU) ---

up: ## Start full stack (GPU required)
	$(COMPOSE_GPU) up -d
	@echo "\n✅ Vision is running at http://localhost"

down: ## Stop all services
	$(COMPOSE_GPU) down
	@echo "\n🛑 Vision stopped"

build: ## Build all custom images
	$(COMPOSE_GPU) build

logs: ## Tail logs for all services
	$(COMPOSE_GPU) logs -f

logs-vllm: ## Tail vLLM logs
	$(COMPOSE_GPU) logs -f vllm

logs-backend: ## Tail backend logs
	$(COMPOSE_GPU) logs -f backend

# --- Development (No GPU) ---

dev: ## Start dev stack (no GPU, mock LLM)
	$(COMPOSE_DEV) up -d
	@echo "\n✅ Vision DEV is running at http://localhost"
	@echo "   Mock LLM active — no GPU required"

dev-down: ## Stop dev stack
	$(COMPOSE_DEV) down

dev-build: ## Build dev images
	$(COMPOSE_DEV) build

dev-logs: ## Tail dev logs
	$(COMPOSE_DEV) logs -f

# --- Model Switching ---

switch-model: ## Switch model profile: make switch-model PROFILE=A|B
	@echo "🔄 Switching to model profile $(PROFILE)..."
	@cp .env.profiles/config-$(shell echo $(PROFILE) | tr A-Z a-z).env .env.active-model
	$(COMPOSE_GPU) up -d vllm
	@echo "✅ Model switched to profile $(PROFILE)"
	@echo "   Waiting for model to load (check: make logs-vllm)"

# --- Testing ---

test: ## Run backend tests
	cd backend && python -m pytest tests/ -v

lint: ## Run linters
	cd backend && ruff check app/
	cd backend && mypy app/

# --- Maintenance ---

clean: ## Remove all data volumes (DESTRUCTIVE!)
	@echo "⚠️  This will DELETE all data volumes!"
	@read -p "Are you sure? [y/N] " confirm && [ "$$confirm" = "y" ] || exit 1
	$(COMPOSE_GPU) down -v
	@echo "🗑️  All volumes removed"

status: ## Show service status
	$(COMPOSE_GPU) ps

health: ## Check API health
	@curl -s http://localhost/api/health | python3 -m json.tool || echo "❌ API not responding"

download-models: ## Download all model weights (run on GPU VM with internet)
	bash scripts/download-models.sh
