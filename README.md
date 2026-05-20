# Microsserviços de Agentes MLOps

Este repositório demonstra uma **Arquitetura Multiagente** utilizando **Microsserviços Compartilhados**. O projeto utiliza o framework **Agno** para orquestração de agentes e **FastAPI** para os microsserviços, com suporte para deploy no Google Cloud Run e execução local via Docker Compose.

## Visão Geral da Arquitetura

O sistema é composto por um Orquestrador central que coordena agentes especializados. Cada agente utiliza ferramentas que, por trás das cenas, realizam chamadas HTTP para microsserviços independentes.

- **Orquestrador (Agno Team):** Gerencia o fluxo de trabalho e decide qual agente chamar.
- **search-svc:** Microsserviço de busca semântica em documentos técnicos.
- **report-svc:** Microsserviço de geração de relatórios formatados em Markdown.
- **Dashboard (React):** Interface visual para interação com os agentes.

---

## Estrutura do Projeto

```text
mlops-agents-microservices/
├── agents/                 # Orquestrador Agno e definições dos Agentes
├── frontend/               # Dashboard React (Vite + TypeScript)
├── microservices/
│   ├── search-svc/         # API de Busca (FastAPI)
│   └── report-svc/         # API de Relatórios (FastAPI)
├── docs/
│   └── deploy-cloud-run.md # Guia detalhado de deploy no GCP
├── scripts/                # Scripts de automação de deploy
├── docker-compose.dev.yml  # Stack completo local (Dev)
├── docker-compose.prod.yml # API + Frontend conectando ao Cloud Run
├── Makefile                # Atalhos para produtividade
└── README.md
```

---

## Pré-requisitos

- **Python >= 3.12** e [**uv**](https://astral.sh/uv/) (gerenciador de pacotes)
- **Node.js** e **npm** (para o frontend)
- **Docker** e **Docker Compose**
- **gcloud CLI** (caso deseje realizar o deploy no GCP)

---

## Configuração Inicial

1. **Instalar dependências:**
   ```bash
   make setup
   ```

2. **Configurar Variáveis de Ambiente:**
   ```bash
   cp .env.example .env
   # Adicione sua GOOGLE_API_KEY (Gemini) no arquivo .env
   ```

---

## Modos de Execução

O projeto suporta dois modos principais de execução via Docker:

### 1. Modo Desenvolvimento (Full Local)
Neste modo, todos os 4 serviços (API, Frontend, Search, Report) rodam localmente em containers.
```bash
make build
make up
# Para encerrar os serviços locais:
make down
```
*Acesse o Dashboard em http://localhost:3000*

---

## Guia de Deploy (Google Cloud Run)

Se você deseja realizar o deploy dos microsserviços no GCP para testar o modo produção ou a escalabilidade serverless, siga as instruções detalhadas no nosso guia:

👉 **[Guia de Deploy no Cloud Run](docs/deploy-cloud-run.md)**

---

### 2. Modo Produção Híbrido (Local -> Cloud Run)
Neste modo, apenas o Orquestrador e o Frontend rodam localmente (ou em containers), mas eles se comunicam com os microsserviços já deployados no **Google Cloud Run**.
```bash
# Certifique-se de que as URLs no .env apontam para o Cloud Run
make build-prod
make up-prod
# Para encerrar os serviços:
make down-prod
```

---

## Comandos Úteis (Makefile)

| Comando | Descrição |
| :--- | :--- |
| `make setup` | Instala dependências (uv + npm) |
| `make up` | Sobe o stack completo local (Dev) |
| `make up-prod` | Sobe Orquestrador + Frontend (conectados ao GCP) |
| `make down` / `make down-prod` | Para os containers do respectivo modo |
| `make logs` | Visualiza logs dos containers locais |
| `make urls` | Exibe as URLs dos serviços no Cloud Run |
| `make health` | Verifica a saúde dos serviços no Cloud Run |
| `make deploy` | Realiza o deploy completo no GCP |

---

## Autor
**Igor Reis Braziel** - [braziel@discente.ufg.br](mailto:braziel@discente.ufg.br)
