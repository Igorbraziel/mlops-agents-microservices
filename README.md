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
├── deploy.sh                   # Script de automação de deploy
├── .env.example
├── .gitignore
├── GEMINI.md                   # Instruções e contexto para Agentes de IA
└── README.md
```

## Pré-requisitos

- CLI `gcloud` (Google Cloud SDK) configurada e autenticada
- `docker` instalado (para builds e testes locais)
- `python >= 3.11`
- `uv` (instalador ultrarrápido de pacotes Python)

## Configuração e Instalação

1. **Instalar o `uv` (caso ainda não esteja instalado):**
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. **Inicializar as dependências:**
   ```bash
   uv sync
   source .venv/bin/activate
   ```

3. **Configurar Variáveis de Ambiente:**
   ```bash
   cp .env.example .env
   # Adicione sua GEMINI_API_KEY e as URLs dos serviços caso já estejam em produção
   ```

## Executando Localmente

Para testar o sistema localmente, você pode iniciar os microsserviços em portas diferentes:

**Terminal 1 (search-svc):**
```bash
cd microservices/search-svc
uv run uvicorn main:app --port 8001 --reload
```

**Terminal 2 (report-svc):**
```bash
cd microservices/report-svc
uv run uvicorn main:app --port 8002 --reload
```

**Terminal 3 (Orquestrador):**
```bash
cd agents
uv run python orchestrator.py
```

## Deploy

O script `deploy.sh` automatiza o deploy dos dois microsserviços no Google Cloud Run. Certifique-se de estar autenticado utilizando `gcloud auth login` e de ter configurado o projeto ativo.

```bash
chmod +x deploy.sh
./deploy.sh
```

Após o deploy, atualize o arquivo `.env` com as novas URLs geradas pelo Cloud Run para permitir que o orquestrador utilize os endpoints de produção em vez de `localhost`.
