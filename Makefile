.PHONY: help setup build up down logs run-demo run-api run-frontend clean \
        deploy deploy-search deploy-report \
        urls health \
        build-prod up-prod down-prod

REGION ?= us-central1

help: ## Exibe esta ajuda
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# ── Desenvolvimento Local ─────────────────────────────────────────────────────

setup: ## Instala as dependências locais (agents, microservices e frontend)
	@echo "📦 Sincronizando dependências do agents..."
	cd agents && uv sync
	@echo "📦 Sincronizando dependências do report-svc..."
	cd microservices/report-svc && uv sync
	@echo "📦 Sincronizando dependências do search-svc..."
	cd microservices/search-svc && uv sync
	@echo "📦 Instalando dependências do frontend..."
	cd frontend && npm install

build: ## Constrói as imagens via Docker Compose (Dev)
	docker compose -f docker-compose.dev.yml build

up: ## Inicia todos os serviços via Docker Compose (Dev)
	docker compose -f docker-compose.dev.yml up -d
	@echo "🚀 Frontend (Dev) disponível em: http://localhost:5173"

down: ## Para e remove os containers (Dev)
	docker compose -f docker-compose.dev.yml down

# ── Setup "Produção" (Local Orchestrator -> Cloud Run Microservices) ──────────

build-prod: ## Constrói as imagens para o modo produção (API + Frontend)
	docker compose -f docker-compose.prod.yml build

up-prod: ## Inicia API e Frontend apontando para o Cloud Run
	docker compose -f docker-compose.prod.yml up -d
	@echo "🚀 Frontend (Prod) disponível em: http://localhost:8080"

down-prod: ## Para os containers do modo produção
	docker compose -f docker-compose.prod.yml down

# ── Utilitários de Execução ───────────────────────────────────────────────────

logs: ## Exibe os logs dos containers locais (Docker Compose)
	docker compose -f docker-compose.dev.yml logs -f

run-demo: ## Executa o orquestrador (CLI) localmente
	cd agents && uv run python orchestrator.py

run-api: ## Executa a API do Orquestrador localmente
	cd agents && uv run python api.py

run-frontend: ## Executa o Dashboard React localmente
	cd frontend && npm run dev

clean: ## Remove arquivos temporários, caches e pastas de build
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf frontend/dist

# ── Cloud Run — Deploy ────────────────────────────────────────────────────────

deploy: ## Faz o deploy de todos os microsserviços no Cloud Run
	bash scripts/deploy.sh

deploy-search: ## Faz o deploy isolado do search-svc no Cloud Run
	bash scripts/deploy-search-svc.sh

deploy-report: ## Faz o deploy isolado do report-svc no Cloud Run
	bash scripts/deploy-report-svc.sh

# ── Cloud Run — Utilitários ───────────────────────────────────────────────────

urls: ## Exibe as URLs dos microsserviços no Cloud Run
	@echo "search-svc: $$(gcloud run services describe search-svc --platform managed --region $(REGION) --format 'value(status.url)' 2>/dev/null || echo 'não deployado')"
	@echo "report-svc: $$(gcloud run services describe report-svc --platform managed --region $(REGION) --format 'value(status.url)' 2>/dev/null || echo 'não deployado')"

health: ## Verifica o health check dos microsserviços no Cloud Run
	@SEARCH_URL=$$(gcloud run services describe search-svc --platform managed --region $(REGION) --format 'value(status.url)' 2>/dev/null); \
	REPORT_URL=$$(gcloud run services describe report-svc --platform managed --region $(REGION) --format 'value(status.url)' 2>/dev/null); \
	echo "🩺 Verificando health checks..."; \
	if curl --silent --fail --max-time 10 "$${SEARCH_URL}/health" | grep -q '"ok"'; then \
	  echo "  ✅ search-svc: OK ($${SEARCH_URL})"; \
	else \
	  echo "  ❌ search-svc: FALHA"; \
	fi; \
	if curl --silent --fail --max-time 10 "$${REPORT_URL}/health" | grep -q '"ok"'; then \
	  echo "  ✅ report-svc: OK ($${REPORT_URL})"; \
	else \
	  echo "  ❌ report-svc: FALHA"; \
	fi
