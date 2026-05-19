.PHONY: help setup build up down logs run-demo run-api run-frontend clean

help: ## Exibe esta ajuda
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

setup: ## Instala as dependências locais via uv e npm
	uv sync
	cd frontend && npm install

build: ## Constrói as imagens via Docker Compose
	docker compose build

up: ## Inicia todos os serviços via Docker Compose
	docker compose up -d

down: ## Para e remove os containers
	docker compose down

logs: ## Exibe os logs dos containers
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
