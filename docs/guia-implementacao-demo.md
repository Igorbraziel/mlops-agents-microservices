# **Guia de Implementação — Opção C: Multi-Agent com Microsserviços Compartilhados**

**Objetivo:** Subir dois microsserviços no Cloud Run, criar dois agentes Agno especializados e um orquestrador que os coordena — demonstrando reutilização de infraestrutura, observabilidade isolada por serviço e uma interface frontend profissional.

## **Arquitetura que vamos construir**

┌─────────────────────────────────────────────────────┐  
│           FRONTEND (React + Vite)                   │  
│  Dashboard profissional com questões de demo        │  
└──────────────────────┬──────────────────────────────┘  
                       │  
                       ▼  
┌─────────────────────────────────────────────────────┐  
│           ORQUESTRADOR API (FastAPI)                │  
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

1. Usuário clica em uma questão de demo no **Frontend**.
2. Frontend chama a **Orquestrador API**.
3. Orquestrador delega para agente-pesquisa no Cloud Run.
4. Orquestrador passa os resultados para agente-relatorio no Cloud Run.
5. Orquestrador retorna o Markdown final para o Frontend exibir com formatação rica.

## **Pré-requisitos**

# Ferramentas necessárias  
gcloud --version        # Google Cloud SDK  
docker --version        # Docker Desktop  
python --version        # Python 3.11+
node --version          # Node.js 18+ (para o frontend)

## **Estrutura de pastas do projeto**

opcao-c-demo/  
├── frontend/          ← Dashboard React + TypeScript
├── microsservicos/  
│   ├── busca-svc/  
│   └── relatorio-svc/  
├── agentes/  
│   ├── search_agent.py  
│   ├── report_agent.py  
│   ├── orchestrator.py  
│   └── api.py         ← Exposição do time como API
├── deploy.sh  
├── .env.example  
├── .env  
└── .gitignore

## **Etapa 1 a 6 — Infraestrutura e Agentes**
*(Siga as etapas originais para deploy dos microsserviços e configuração dos agentes individuais)*

## **Etapa 7 — Orquestrador como API (api.py)**

Para que o frontend possa se comunicar com o time de agentes, expomos o orquestrador via FastAPI.

### **agentes/api.py**

```python
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from orchestrator import orchestrator

app = FastAPI(title="MLOps Orchestrator API")

# Habilitar CORS para o frontend local
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str

@app.post("/chat")
async def chat(request: ChatRequest):
    try:
        response = orchestrator.run(request.message)
        return {"content": str(response.content)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

## **Etapa 8 — Frontend Profissional (React)**

O frontend utiliza React, Vite e Tailwind-like CSS para uma experiência moderna.

### **Comandos para inicializar:**
```bash
cd frontend
npm install
npm install react-markdown
npm run dev
```

### **Destaques do Frontend:**
- **Demo Questions:** Botões prontos para disparar fluxos complexos.
- **Markdown Rendering:** Visualização limpa dos relatórios gerados.
- **Typing Indicators:** Feedback visual enquanto os agentes trabalham.

## **Etapa 9 — Rodando a Demo Completa**

Para a apresentação, você precisará de 3 terminais:

1. **Terminal 1 (API):**
   ```bash
   cd agentes
   uv run python api.py
   ```

2. **Terminal 2 (Frontend):**
   ```bash
   cd frontend
   npm run dev
   ```

3. **Terminal 3 (Logs):**
   Acompanhe os logs dos microsserviços no Cloud Run para mostrar a orquestração em tempo real.

## **O que mostrar na apresentação**

1. **Interface:** Mostre o Dashboard e as questões de demo.
2. **Interação:** Clique em "Full Report" e mostre o `show_progress` no terminal da API enquanto o frontend espera.
3. **Resultado:** Mostre o relatório formatado aparecendo no dashboard.
4. **Isolamento:** Mostre que o Frontend fala com a API, que fala com Agentes, que falam com Microsserviços — a separação total de responsabilidades.
