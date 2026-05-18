# **Guia de Implementação — Opção C: Multi-Agent com Microsserviços Compartilhados**

**Objetivo:** Subir dois microsserviços no Cloud Run, criar dois agentes Agno especializados

e um orquestrador que os coordena — demonstrando reutilização de infraestrutura e

observabilidade isolada por serviço.

## **Arquitetura que vamos construir**

┌─────────────────────────────────────────────────────┐  
│           ORQUESTRADOR (local ou Cloud Run)         │  
│  Agno Team / Agent que coordena os sub-agentes      │  
└──────────────────────┬──────────────────────────────┘  
                       │  
          ┌────────────┴────────────┐  
          ▼                         ▼  
┌──────────────────┐     ┌───────────────────┐  
│  agente-pesquisa │     │  agente-relatorio │  
│  (Agno Agent)    │     │  (Agno Agent)     │  
└────────┬─────────┘     └─────────┬─────────┘  
         │                         │  
         ▼                         ▼  
┌──────────────────┐     ┌───────────────────┐  
│   Cloud Run      │     │    Cloud Run      │  
│   busca-svc      │     │   relatorio-svc   │  
│  POST /search    │     │  POST /generate   │  
└──────────────────┘     └───────────────────┘

**Fluxo de uma requisição:**

1. Usuário pede: *"Pesquise sobre cold starts e gere um relatório resumido"*  
2. Orquestrador delega para agente-pesquisa  
3. agente-pesquisa chama busca-svc no Cloud Run → recebe resultados  
4. Orquestrador passa os resultados para agente-relatorio  
5. agente-relatorio chama relatorio-svc no Cloud Run → recebe o PDF/markdown  
6. Orquestrador retorna o resultado final ao usuário

## **Pré-requisitos**

\# Ferramentas necessárias  
gcloud \--version        \# Google Cloud SDK  
docker \--version        \# Docker Desktop  
python \--version        \# Python 3.11+

\# Autenticação no GCP  
gcloud auth login  
gcloud config set project SEU\_PROJECT\_ID

\# Habilitar APIs necessárias  
gcloud services enable run.googleapis.com \\  
                       secretmanager.googleapis.com \\  
                       artifactregistry.googleapis.com \\  
                       cloudbuild.googleapis.com

\# Instalar o uv (gerenciador de pacotes ultrarrápido em Rust)  
curl \-LsSf \[https://astral.sh/uv/install.sh\](https://astral.sh/uv/install.sh) | sh

\# Inicializar o projeto com uv e adicionar dependências
uv init
uv add agno fastapi uvicorn httpx google-generativeai python-dotenv
source .venv/bin/activate

## **Estrutura de pastas do projeto**

opcao-c-demo/  
├── microsservicos/  
│   ├── busca-svc/  
│   │   ├── main.py  
│   │   ├── pyproject.toml  
│   │   └── Dockerfile  
│   └── relatorio-svc/  
│       ├── main.py  
│       ├── pyproject.toml  
│       └── Dockerfile  
├── agentes/  
│   ├── agente\_pesquisa.py  
│   ├── agente\_relatorio.py  
│   └── orquestrador.py  
├── deploy.sh          ← script de automação via CLI  
├── .env.example  
├── .env               ← nunca commitar  
└── .gitignore

## **Etapa 1 — Microsserviço de Busca (busca-svc)**

Este serviço recebe uma query e retorna documentos relevantes.

Para a demo, usamos uma base de conhecimento em memória sobre os tópicos da aula.

### **microsservicos/busca-svc/main.py**

from fastapi import FastAPI  
from pydantic import BaseModel

app \= FastAPI(title="Busca Semântica \- Demo")

\# Base de conhecimento em memória (em produção: Qdrant, pgvector, etc.)  
BASE\_CONHECIMENTO \= \[  
    {  
        "id": 1,  
        "titulo": "Cold Start no Cloud Run",  
        "conteudo": (  
            "Cold start é o tempo de inicialização de uma instância serverless quando "  
            "não há instâncias ativas. Pode levar de 200ms a 3s. Fatores que aumentam: "  
            "imagens Docker grandes, imports pesados como torch e tensorflow. "  
            "Mitigação: min-instances, imagens leves, lazy loading."  
        ),  
        "tags": \["serverless", "cloud run", "cold start", "performance"\],  
    },  
    {  
        "id": 2,  
        "titulo": "Microsserviços vs Monolito",  
        "conteudo": (  
            "Microsserviços são unidades pequenas e independentes com responsabilidade única. "  
            "Cada serviço é deployável, escalável e falha de forma isolada. "  
            "Monolito é mais simples para times pequenos e POCs, mas difícil de escalar "  
            "partes individuais. Microsserviços são ideais para produção com múltiplas equipes."  
        ),  
        "tags": \["microsserviços", "monolito", "arquitetura"\],  
    },  
    {  
        "id": 3,  
        "titulo": "Secrets Management com GCP Secret Manager",  
        "conteudo": (  
            "Secrets nunca devem existir no código ou na imagem Docker. "  
            "O GCP Secret Manager armazena secrets versionados e auditados. "  
            "O Cloud Run injeta como variável de ambiente em runtime via \--set-secrets. "  
            "Princípio do menor privilégio: cada microsserviço acessa apenas os secrets que precisa."  
        ),  
        "tags": \["secrets", "segurança", "gcp", "iam"\],  
    },  
    {  
        "id": 4,  
        "titulo": "Pipeline vs Microsserviços em MLOps",  
        "conteudo": (  
            "Pipeline: sequencial e acoplado, ideal para ETL e treinamento de modelos. "  
            "Microsserviços: sob demanda e desacoplado, ideal para APIs e tools de agentes. "  
            "Treinamento de modelos usa pipeline. Servir o modelo como tool de agente usa microsserviço."  
        ),  
        "tags": \["pipeline", "mlops", "arquitetura", "agentes"\],  
    },  
    {  
        "id": 5,  
        "titulo": "Agentes com Tools como Microsserviços",  
        "conteudo": (  
            "Cada tool do agente pode ser um microsserviço independente no Cloud Run. "  
            "Benefícios: observabilidade individual por tool, escala independente, "  
            "reutilização entre múltiplos agentes, isolamento de falhas, flexibilidade tecnológica. "  
            "O agente Agno faz chamadas HTTP para os endpoints dos microsserviços."  
        ),  
        "tags": \["agentes", "tools", "cloud run", "agno"\],  
    },  
\]

class BuscaRequest(BaseModel):  
    query: str  
    top\_k: int \= 3

def buscar\_por\_relevancia(query: str, top\_k: int) \-\> list\[dict\]:  
    """Busca simples por palavras-chave. Em produção: embeddings \+ similaridade vetorial."""  
    query\_lower \= query.lower()  
    resultados \= \[\]

    for doc in BASE\_CONHECIMENTO:  
        score \= 0  
        for palavra in query\_lower.split():  
            if palavra in doc\["titulo"\].lower():  
                score \+= 3  
            if palavra in doc\["conteudo"\].lower():  
                score \+= 1  
            if any(palavra in tag for tag in doc\["tags"\]):  
                score \+= 2

        if score \> 0:  
            resultados.append({\*\*doc, "score": score})

    resultados.sort(key=lambda x: x\["score"\], reverse=True)  
    return resultados\[:top\_k\]

@app.post("/search")  
def search(req: BuscaRequest) \-\> dict:  
    resultados \= buscar\_por\_relevancia(req.query, req.top\_k)  
    return {  
        "query": req.query,  
        "total": len(resultados),  
        "resultados": resultados,  
    }

@app.get("/health")  
def health() \-\> dict:  
    return {"status": "ok", "servico": "busca-svc"}

### **microsservicos/busca-svc/pyproject.toml**

```toml
[project]
name = "busca-svc"
version = "0.1.0"
description = "Microsserviço de Busca"
requires-python = ">=3.11"
dependencies = [
    "fastapi>=0.115.0",
    "uvicorn[standard]>=0.30.6",
    "pydantic>=2.9.2"
]
```

### **microsservicos/busca-svc/Dockerfile**

```dockerfile
FROM python:3.12-slim

# Copia o binário do uv diretamente da imagem oficial
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Variáveis para otimização do uv
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy

# Instala dependências
COPY pyproject.toml uv.lock* ./
RUN uv sync --frozen --no-install-project --no-dev

# Copia o código da aplicação
COPY main.py .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
```

### **Testando localmente antes do deploy**

cd microsservicos/busca-svc  
uv run uvicorn main:app \--reload \--port 8001

\# Em outro terminal:  
curl \-X POST http://localhost:8001/search \\  
  \-H "Content-Type: application/json" \\  
  \-d '{"query": "cold start serverless", "top\_k": 2}'

## **Etapa 2 — Microsserviço de Relatório (relatorio-svc)**

Este serviço recebe dados estruturados e gera um relatório formatado em markdown.

### **microsservicos/relatorio-svc/main.py**

from fastapi import FastAPI  
from pydantic import BaseModel  
from datetime import datetime

app \= FastAPI(title="Gerador de Relatórios \- Demo")

class DocumentoInput(BaseModel):  
    titulo: str  
    conteudo: str

class RelatorioRequest(BaseModel):  
    titulo\_relatorio: str  
    autor: str  
    documentos: list\[DocumentoInput\]  
    instrucoes\_adicionais: str \= ""

@app.post("/generate")  
def gerar\_relatorio(req: RelatorioRequest) \-\> dict:  
    """Gera um relatório estruturado em Markdown a partir dos documentos recebidos."""  
    agora \= datetime.now().strftime("%d/%m/%Y %H:%M")

    linhas \= \[  
        f"\# {req.titulo\_relatorio}",  
        f"",  
        f"\*\*Autor:\*\* {req.autor}  ",  
        f"\*\*Gerado em:\*\* {agora}  ",  
        f"\*\*Total de fontes:\*\* {len(req.documentos)}",  
        f"",  
        "---",  
        "",  
        "\#\# Sumário Executivo",  
        "",  
        f"Este relatório consolida {len(req.documentos)} documento(s) sobre o tema \*\*{req.titulo\_relatorio}\*\*.",  
        "",  
    \]

    if req.instrucoes\_adicionais:  
        linhas \+= \[  
            "\#\#\# Contexto Adicional",  
            "",  
            req.instrucoes\_adicionais,  
            "",  
        \]

    linhas \+= \["\#\# Documentos Analisados", ""\]

    for i, doc in enumerate(req.documentos, 1):  
        linhas \+= \[  
            f"\#\#\# {i}. {doc.titulo}",  
            "",  
            doc.conteudo,  
            "",  
        \]

    linhas \+= \[  
        "---",  
        "",  
        "\*Relatório gerado automaticamente pelo relatorio-svc\*",  
    \]

    markdown \= "\\n".join(linhas)

    return {  
        "titulo": req.titulo\_relatorio,  
        "gerado\_em": agora,  
        "total\_documentos": len(req.documentos),  
        "markdown": markdown,  
        "caracteres": len(markdown),  
    }

@app.get("/health")  
def health() \-\> dict:  
    return {"status": "ok", "servico": "relatorio-svc"}

### **microsservicos/relatorio-svc/pyproject.toml**

```toml
[project]
name = "relatorio-svc"
version = "0.1.0"
description = "Microsserviço de Relatório"
requires-python = ">=3.11"
dependencies = [
    "fastapi>=0.115.0",
    "uvicorn[standard]>=0.30.6",
    "pydantic>=2.9.2"
]
```

### **microsservicos/relatorio-svc/Dockerfile**

```dockerfile
FROM python:3.12-slim

# Copia o binário do uv diretamente da imagem oficial
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Variáveis para otimização do uv
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy

# Instala dependências
COPY pyproject.toml uv.lock* ./
RUN uv sync --frozen --no-install-project --no-dev

# Copia o código da aplicação
COPY main.py .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
```

## **Etapa 3 — Deploy Automatizado via CLI (deploy.sh)**

Em vez de rodar comandos manuais soltos, vamos usar um script de automação estruturado para o deploy. Isso demonstra maturidade de engenharia.

Crie o arquivo deploy.sh na raiz do projeto:

### **deploy.sh**

\#\!/bin/bash

\# Cores para o terminal  
GREEN='\\033\[0;32m'  
BLUE='\\033\[0;34m'  
NC='\\033\[0m'

PROJECT\_ID=$(gcloud config get-value project)  
REGION="us-central1"

echo \-e "${BLUE}🚀 Iniciando deploy dos microsserviços no projeto: ${PROJECT\_ID}${NC}\\n"

\# ── Deploy do busca-svc ──────────────────────────────────────────────────────  
echo \-e "${GREEN}📦 Fazendo deploy do busca-svc...${NC}"  
gcloud run deploy busca-svc \\  
  \--source ./microsservicos/busca-svc \\  
  \--region $REGION \\  
  \--allow-unauthenticated \\  
  \--memory 512Mi \\  
  \--cpu 1 \\  
  \--min-instances 0 \\  
  \--max-instances 2 \\  
  \--quiet

BUSCA\_URL=$(gcloud run services describe busca-svc \--platform managed \--region $REGION \--format 'value(status.url)')  
echo \-e "${GREEN}✅ busca-svc online em: ${BUSCA\_URL}${NC}\\n"

\# ── Deploy do relatorio-svc ──────────────────────────────────────────────────  
echo \-e "${GREEN}📄 Fazendo deploy do relatorio-svc...${NC}"  
gcloud run deploy relatorio-svc \\  
  \--source ./microsservicos/relatorio-svc \\  
  \--region $REGION \\  
  \--allow-unauthenticated \\  
  \--memory 512Mi \\  
  \--cpu 1 \\  
  \--min-instances 0 \\  
  \--max-instances 2 \\  
  \--quiet

RELATORIO\_URL=$(gcloud run services describe relatorio-svc \--platform managed \--region $REGION \--format 'value(status.url)')  
echo \-e "${GREEN}✅ relatorio-svc online em: ${RELATORIO\_URL}${NC}\\n"

\# ── Verificação de Health Check ──────────────────────────────────────────────  
echo \-e "${BLUE}🩺 Realizando Health Check...${NC}"  
curl \-s "$BUSCA\_URL/health" | grep \-q "ok" && echo \-e "busca-svc: ${GREEN}OK${NC}" || echo "busca-svc: FALHA"  
curl \-s "$RELATORIO\_URL/health" | grep \-q "ok" && echo \-e "relatorio-svc: ${GREEN}OK${NC}" || echo "relatorio-svc: FALHA"

echo \-e "\\n${BLUE}🎯 Deploy concluído\! Atualize seu arquivo .env com as URLs acima.${NC}"

### **Executando o Deploy**

\# Dê permissão de execução ao script  
chmod \+x deploy.sh

\# Rode o script  
./deploy.sh

**Dica para a apresentação:** execute o script e deixe ele rodando enquanto você abre o Console do GCP. Mostre as URLs geradas e as métricas de instâncias subindo (argumento de observabilidade na prática).

## **Etapa 4 — Configurar a Chave do Gemini como Secret (opcional mas recomendado)**

\# Criar o secret  
gcloud secrets create GEMINI\_API\_KEY \--replication-policy="automatic"

\# Adicionar o valor (obtido em \[https://aistudio.google.com/app/apikey\](https://aistudio.google.com/app/apikey))  
echo \-n "SUA\_CHAVE\_AQUI" | gcloud secrets versions add GEMINI\_API\_KEY \--data-file=-

\# Verificar  
gcloud secrets versions list GEMINI\_API\_KEY

Para a demo local, basta colocar no .env. O Secret Manager é para mostrar o conceito

à audiência — a Pessoa 3 já vai ter explicado como funciona.

## **Etapa 5 — Agente de Pesquisa**

### **agentes/agente\_pesquisa.py**

import httpx  
from agno.agent import Agent  
from agno.models.google import Gemini  
from agno.tools import tool  
import os

BUSCA\_SVC\_URL \= os.environ\["BUSCA\_SVC\_URL"\]

@tool(description=(  
    "Busca documentos relevantes na base de conhecimento sobre MLOps, "  
    "serverless, microsserviços e agentes. Use quando precisar de informações "  
    "técnicas sobre esses temas. Retorna lista de documentos com título e conteúdo."  
))  
def buscar\_documentos(query: str, top\_k: int \= 3\) \-\> dict:  
    """Chama o microsserviço de busca semântica no Cloud Run."""  
    response \= httpx.post(  
        f"{BUSCA\_SVC\_URL}/search",  
        json={"query": query, "top\_k": top\_k},  
        timeout=15.0,  
    )  
    response.raise\_for\_status()  
    return response.json()

agente\_pesquisa \= Agent(  
    name="Agente Pesquisador",  
    model=Gemini(id="gemini-2.0-flash"),  
    tools=\[buscar\_documentos\],  
    instructions=\[  
        "Você é um especialista em pesquisa técnica sobre MLOps e arquiteturas de IA.",  
        "Quando receber uma pergunta, use a tool buscar\_documentos para encontrar informações relevantes.",  
        "Retorne os resultados de forma estruturada: liste os documentos encontrados com título e resumo.",  
        "Sempre indique quantos documentos foram encontrados.",  
    \],  
    markdown=True,  
)

## **Etapa 6 — Agente de Relatório**

### **agentes/agente\_relatorio.py**

import httpx  
from agno.agent import Agent  
from agno.models.google import Gemini  
from agno.tools import tool  
import os

RELATORIO\_SVC\_URL \= os.environ\["RELATORIO\_SVC\_URL"\]

@tool(description=(  
    "Gera um relatório estruturado em Markdown a partir de uma lista de documentos. "  
    "Use quando precisar consolidar informações pesquisadas em um documento formatado. "  
    "Recebe título, autor e lista de documentos com título e conteúdo."  
))  
def gerar\_relatorio(  
    titulo\_relatorio: str,  
    autor: str,  
    documentos: list\[dict\],  
    instrucoes\_adicionais: str \= "",  
) \-\> dict:  
    """Chama o microsserviço de geração de relatórios no Cloud Run."""  
    response \= httpx.post(  
        f"{RELATORIO\_SVC\_URL}/generate",  
        json={  
            "titulo\_relatorio": titulo\_relatorio,  
            "autor": autor,  
            "documentos": documentos,  
            "instrucoes\_adicionais": instrucoes\_adicionais,  
        },  
        timeout=15.0,  
    )  
    response.raise\_for\_status()  
    return response.json()

agente\_relatorio \= Agent(  
    name="Agente Relator",  
    model=Gemini(id="gemini-2.0-flash"),  
    tools=\[gerar\_relatorio\],  
    instructions=\[  
        "Você é especialista em criar relatórios técnicos claros e bem estruturados.",  
        "Quando receber documentos para consolidar, use a tool gerar\_relatorio.",  
        "Sempre formate os documentos como lista de dicts com 'titulo' e 'conteudo'.",  
        "Após gerar o relatório, exiba o campo 'markdown' do resultado.",  
    \],  
    markdown=True,  
)

## **Etapa 7 — Orquestrador (a peça central da demo)**

### **agentes/orquestrador.py**

import os  
from dotenv import load\_dotenv

load\_dotenv()  \# carrega .env em desenvolvimento local

from agno.agent import Agent  
from agno.models.google import Gemini  
from agno.team import Team  \# orquestração nativa do Agno

from agente\_pesquisa import agente\_pesquisa  
from agente\_relatorio import agente\_relatorio

\# ── Orquestrador como Team no Agno ──────────────────────────────────────────  
\# O Team coordena múltiplos agentes: decide qual chamar e em que ordem.  
orquestrador \= Team(  
    name="Orquestrador MLOps",  
    mode="coordinate",          \# o orquestrador decide quem faz o quê  
    model=Gemini(id="gemini-2.0-flash"),  
    members=\[agente\_pesquisa, agente\_relatorio\],  
    instructions=\[  
        "Você coordena dois agentes especializados:",  
        "- 'Agente Pesquisador': busca informações técnicas na base de conhecimento",  
        "- 'Agente Relator': gera relatórios estruturados a partir de informações",  
        "",  
        "Fluxo padrão para pedidos de relatório:",  
        "1. Chame o Agente Pesquisador para buscar os documentos relevantes",  
        "2. Passe os resultados para o Agente Relator para gerar o relatório",  
        "3. Apresente o relatório final ao usuário",  
        "",  
        "Para perguntas simples sem necessidade de relatório, use apenas o Agente Pesquisador.",  
    \],  
    markdown=True,  
    show\_progress=True,     \# mostra qual agente está sendo chamado (ótimo para demo\!)  
)

\# ── Exemplos de uso ──────────────────────────────────────────────────────────  
if \_\_name\_\_ \== "\_\_main\_\_":

    print("\\n" \+ "="\*60)  
    print("DEMO 1: Pesquisa simples (apenas agente-pesquisa)")  
    print("="\*60)  
    orquestrador.print\_response(  
        "O que são microsserviços e qual a diferença para um pipeline?",  
        stream=True,  
    )

    print("\\n" \+ "="\*60)  
    print("DEMO 2: Pesquisa \+ Relatório (ambos os agentes)")  
    print("="\*60)  
    orquestrador.print\_response(  
        "Pesquise sobre segurança de secrets e cold starts, "  
        "depois gere um relatório chamado 'Boas Práticas em Produção' com o que encontrar. "  
        "Autor: Grupo MLOps CEIA-UFG",  
        stream=True,  
    )

## **Etapa 8 — Configurar .env e rodar**

### **.env.example (commitado)**

GEMINI\_API\_KEY=your-gemini-key-here  
BUSCA\_SVC\_URL=\[https://busca-svc-xxxxxxxx-uc.a.run.app\](https://busca-svc-xxxxxxxx-uc.a.run.app)  
RELATORIO\_SVC\_URL=\[https://relatorio-svc-xxxxxxxx-uc.a.run.app\](https://relatorio-svc-xxxxxxxx-uc.a.run.app)

### **.env (nunca commitado)**

GEMINI\_API\_KEY=AIzaSy...  
BUSCA\_SVC\_URL=https://busca-svc-...  
RELATORIO\_SVC\_URL=https://relatorio-svc-...

### **.gitignore**

.env  
\_\_pycache\_\_/  
\*.pyc  
.venv/

### **Rodando o orquestrador**

Certifique-se de estar com o ambiente virtual do uv ativo:

cd agentes  
python orquestrador.py

## **Etapa 9 — O que mostrar na apresentação**

### **9.1 — Mostrar os dois serviços no ar (Cloud Run Console)**

* Abra console.cloud.google.com \> Cloud Run  
* Mostre **dois serviços separados**, cada um com sua URL  
* Destaque: *"São dois deploys independentes. Posso atualizar um sem tocar no outro."*

### **9.2 — Rodar a Demo 1 ao vivo**

python orquestrador.py

Deixe o show\_progress=True para o grupo ver qual agente está sendo chamado em tempo real.

### **9.3 — Mostrar os logs separados (o momento mais impactante)**

\# Terminal 1: logs do busca-svc  
gcloud logging read "resource.labels.service\_name=busca-svc" \\  
  \--limit=10 \--format="value(textPayload)"

\# Terminal 2: logs do relatorio-svc  
gcloud logging read "resource.labels.service\_name=relatorio-svc" \\  
  \--limit=10 \--format="value(textPayload)"

Ou mostre no Console: Cloud Run \> busca-svc \> Logs.

**Ponto de fala:** *"Percebam: eu consigo ver exatamente quantas vezes cada tool foi chamada, com que latência, e qualquer erro — isoladamente, sem misturar com os logs do agente."*

## **Roteiro de fala sugerido (10–12 minutos)**

| Tempo | O que fazer |
| :---- | :---- |
| 0–1min | Recapitular: *"Vocês viram serverless, microsserviços e secrets. Agora vamos ver tudo junto."* Mostrar o diagrama da arquitetura. |
| 1–3min | Mostrar o código do busca-svc (30 linhas) e destacar o Dockerfile usando uv para builds otimizados. |
| 3–4min | Mostrar o deploy.sh em execução e os serviços no ar no Console do GCP. |
| 4–6min | Mostrar o código do orquestrador. Explicar o Team do Agno e o desacoplamento das ferramentas. |
| 6–9min | Rodar ao vivo — Demo 1 (só pesquisa) e Demo 2 (pesquisa \+ relatório). |
| 9–11min | Mostrar os logs separados no Console. Fazer o argumento definitivo sobre observabilidade em microsserviços. |
| 11–12min | *"Dois agentes, dois microsserviços, um orquestrador. Reutilização de infra total."* Passar para a Pessoa 3\. |

## **Troubleshooting rápido**

| Problema | Solução |
| :---- | :---- |
| ModuleNotFoundError: agno | uv pip install agno com o venv ativado |
| httpx.ConnectError | Verificar se as URLs no .env estão corretas |
| Error 403 no Cloud Run | Checar se o serviço está com \--allow-unauthenticated |
| gcloud: command not found | Instalar Google Cloud SDK |
| Deploy falha por permissão | gcloud auth login e verificar se o projeto está no CLI |
| Gemini retorna erro de API | Verificar GEMINI\_API\_KEY no .env |

