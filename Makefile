.PHONY: help setup build up down logs run-demo

help: ## Exibe esta ajuda
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

setup: ## Instala as dependências locais via uv
	uv sync

build: ## Constrói as imagens dos microsserviços via Docker Compose
	docker compose build

up: ## Inicia os microsserviços em background
	docker compose up -d

down: ## Para e remove os containers
	docker compose down

logs: ## Exibe os logs dos microsserviços
	docker compose logs -f

run-demo: ## Executa o orquestrador localmente contra os containers
	cd agents && uv run python orchestrator.py

clean: ## Remove arquivos temporários e caches de Python
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
