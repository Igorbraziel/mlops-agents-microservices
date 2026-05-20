# Deploy no Cloud Run — Guia para o Grupo de MLOps

> **Objetivo:** Implantar os microsserviços `search-svc` e `report-svc` no Google Cloud Run e acompanhar os logs via console do GCP durante a apresentação.

---

## Pré-requisitos

Antes de começar, verifique se as ferramentas estão instaladas:

```bash
gcloud --version   # Google Cloud SDK
docker --version   # Docker (usado no build via Cloud Build)
make --version     # Make (para os atalhos do Makefile)
```

---

## 1. Configuração Inicial do GCP

### 1.1 Login e seleção do projeto

```bash
# Autenticar no Google Cloud
gcloud auth login

# Configurar o projeto (substitua pelo seu Project ID)
gcloud config set project SEU_PROJECT_ID

# Confirmar projeto ativo
gcloud config get-value project
```

### 1.2 Habilitar as APIs necessárias

```bash
gcloud services enable \
  run.googleapis.com \
  cloudbuild.googleapis.com \
  artifactregistry.googleapis.com
```

---

## 2. Estrutura dos Microsserviços

```
microservices/
├── search-svc/        ← API de busca semântica
└── report-svc/        ← API de geração de relatórios
```

Cada microsserviço expõe dois endpoints principais:
- `GET /health` — verifica se o serviço está operante.
- `POST /search` ou `POST /generate` — funcionalidades principais.

---

## 3. Deploy

### 3.1 Deploy de todos os microsserviços (recomendado)

```bash
make deploy
```

O script realiza o deploy de ambos os serviços no Cloud Run e exibe as URLs finais.

### 3.2 Deploy individual

```bash
# Apenas o search-svc
make deploy-search

# Apenas o report-svc
make deploy-report
```

---

## 4. Verificar URLs e Status

Após o deploy, veja as URLs dos serviços:

```bash
make urls
```

Para verificar se os serviços estão respondendo corretamente:

```bash
make health
```

---

## 5. Visualizar Logs (GCP Console)

Para acompanhar o que acontece nos microsserviços em tempo real, utilize a interface do Google Cloud Console. Isso permite visualizar erros e o fluxo de dados sem depender de componentes locais do gcloud.

### Passo a passo:
1. Acesse o [Console do Google Cloud](https://console.cloud.google.com/).
2. No menu lateral, navegue até **Cloud Run**.
3. Clique no nome do serviço desejado (`search-svc` ou `report-svc`).
4. Clique na aba **Logs**.
5. (Opcional) Utilize o filtro de "Severidade" para isolar erros ou o campo de busca para filtrar requisições específicas.

---

## 6. Configuração do Orquestrador e Frontend

Após o deploy, você deve configurar o Orquestrador para apontar para os serviços no Cloud Run.

1. **Atualize o `.env`**: Copie as URLs geradas pelo `make urls` para o arquivo `.env` na raiz do projeto.
2. **Inicie os serviços em modo "produção"**: Utilize o Makefile para rodar o orquestrador e o dashboard em segundo plano, já conectados aos serviços live no GCP:

```bash
make up-prod
```

Este comando utiliza o `docker-compose.prod.yml` para subir apenas o que é necessário localmente.

---

## 7. Roteiro para a Apresentação

**Terminal 1 — Orquestrador e Frontend (Background):**
```bash
make up-prod
```

**Navegador — Logs e Interface:**
1. Abra o Console do GCP na aba de Logs do `search-svc`.
2. Abra o Dashboard (geralmente em `http://localhost:3000`).
3. Dispare uma pergunta e mostre os logs aparecendo no navegador.

### O que mostrar ao grupo
1. **Arquitetura Desacoplada:** Explique que o Orquestrador está local (ou em outro container) enquanto os motores de Busca e Relatório estão escalando de forma independente no Cloud Run.
2. **Observabilidade:** Mostre como o Cloud Run facilita a visualização de logs e métricas via interface web.
3. **Escalabilidade:** Comente que o Cloud Run escala para zero quando não há requisições, economizando custos.

---

## 8. Comandos de Referência Rápida

| Comando | O que faz |
|---|---|
| `make deploy` | Deploy de todos os microsserviços |
| `make up-prod` | Inicia Orquestrador + Frontend (conectados ao GCP) |
| `make down-prod` | Para os serviços de produção |
| `make urls` | Exibe as URLs no Cloud Run |
| `make health` | Verifica os health checks |
| `make up` | Inicia todo o stack localmente (Dev) |

---

## 9. Troubleshooting

### ❌ Cold start lento na primeira requisição
Comportamento esperado em serviços com `--min-instances 0`. A primeira requisição pode levar alguns segundos para inicializar.
