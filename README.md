# Microsserviços de Agentes MLOps

## Visão Geral da Arquitetura

Este repositório demonstra uma **Arquitetura Multiagente** utilizando **Microsserviços Compartilhados**. Ele realiza o deploy de dois microsserviços independentes no Google Cloud Run e os coordena utilizando um orquestrador `agno` com dois agentes especializados.

Essa estrutura demonstra:
- Reutilização de ferramentas dos agentes.
- Escalabilidade independente de funcionalidades específicas.
- Observabilidade e métricas isoladas por serviço.

### Fluxo do Sistema
1. **Usuário solicita:** "Pesquise sobre cold starts e gere um relatório resumido."
2. O **Orquestrador** delega a tarefa para o **Agente de Pesquisa**.
3. O **Agente de Pesquisa** faz uma chamada HTTP para o `search-svc` no Cloud Run e recebe os resultados.
4. O **Orquestrador** envia os resultados para o **Agente de Relatórios**.
5. O **Agente de Relatórios** faz uma chamada HTTP para o `report-svc` no Cloud Run e recebe o relatório em Markdown.
6. O **Orquestrador** retorna o resultado final formatado para o usuário.

## Estrutura do Projeto

```text
mlops-agents-microservices/
├── microservices/
│   ├── search-svc/             # Responsável por buscas semânticas (Base de conhecimento mockada)
│   │   ├── main.py
│   │   ├── pyproject.toml
│   │   └── Dockerfile
│   └── report-svc/             # Gera relatórios em Markdown a partir do contexto
│       ├── main.py
│       ├── pyproject.toml
│       └── Dockerfile
├── agents/
│   ├── search_agent.py         # Agente especializado em pesquisa
│   ├── report_agent.py         # Agente especializado em geração de relatórios
│   └── orchestrator.py         # Coordenador central (agno Team)
├── scripts/
│   └── deploy.sh               # Script de automação de deploy
├── .env.example
├── .gitignore
├── docker-compose.yml          # Orquestração de containers local
├── Makefile                    # Atalhos para comandos comuns
├── GEMINI.md                   # Instruções e contexto para Agentes de IA
└── README.md
```

## Pré-requisitos

- CLI `gcloud` (Google Cloud SDK) configurada e autenticada
- `docker` e `docker compose` instalados
- `python >= 3.12`
- `uv` (instalador ultrarrápido de pacotes Python)
- `make`

## Configuração e Instalação

1. **Instalar o `uv` (caso ainda não esteja instalado):**
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. **Inicializar o ambiente:**
   ```bash
   make setup
   ```

3. **Configurar Variáveis de Ambiente:**
   ```bash
   cp .env.example .env
   # Adicione sua GEMINI_API_KEY no arquivo .env
   ```

## Executando Localmente

A forma mais simples de executar o projeto completo é utilizando o `docker-compose` via `Makefile`.

1. **Construir e iniciar os microsserviços:**
   ```bash
   make build
   make up
   ```
   *Os serviços estarão disponíveis em http://localhost:8001 (search-svc) e http://localhost:8002 (report-svc). Ao acessar a raiz de cada serviço, você será redirecionado para a documentação Swagger.*

2. **Executar o Orquestrador (Demo):**
   ```bash
   make run-demo
   ```

## Comandos Úteis (Makefile)

- `make up`: Inicia os containers em background.
- `make down`: Para e remove os containers.
- `make logs`: Visualiza os logs dos serviços em tempo real.
- `make run-demo`: Executa os agentes localmente.
- `make clean`: Limpa caches do Python.

## Deploy

O script `scripts/deploy.sh` automatiza o deploy no Google Cloud Run.

```bash
chmod +x scripts/deploy.sh
./scripts/deploy.sh
```

Após o deploy, atualize as URLs no arquivo `.env` para apontar para os endereços do Cloud Run em vez do `localhost`.
