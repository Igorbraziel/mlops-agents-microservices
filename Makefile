.PHONY: help setup build up down logs run-demo run-api run-frontend clean \
        deploy deploy-search deploy-report \
        logs-search logs-report logs-all \
        urls health

REGION ?= us-central1

help: ## Exibe esta ajuda
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# ── Desenvolvimento Local ─────────────────────────────────────────────────────

setup: ## Instala as dependências locais via uv e npm
	uv sync
	cd frontend && npm install

build: ## Constrói as imagens via Docker Compose
	docker compose build

up: ## Inicia todos os serviços via Docker Compose
	docker compose up -d

down: ## Para e remove os containers
	docker compose down

logs: ## Exibe os logs dos containers locais (Docker Compose)
	docker compose logs -f

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

# ── Cloud Run — Logs ──────────────────────────────────────────────────────────

logs-search: ## Exibe os logs em tempo real do search-svc no Cloud Run
	gcloud run services logs tail search-svc --region $(REGION)

logs-report: ## Exibe os logs em tempo real do report-svc no Cloud Run
	gcloud run services logs tail report-svc --region $(REGION)

logs-all: ## Exibe logs de ambos os serviços em paralelo (Ctrl+C para parar)
	@echo "Iniciando logs em paralelo (search-svc | report-svc)..."
	@gcloud run services logs tail search-svc --region $(REGION) | sed 's/^/[search-svc] /' & \
	 gcloud run services logs tail report-svc --region $(REGION) | sed 's/^/[report-svc] /' & \
	 wait

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
