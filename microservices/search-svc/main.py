from typing import List, Dict, Any
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from pydantic import BaseModel

app = FastAPI(
    title="Busca Semântica - Demo",
    description="Microserviço de busca utilizando uma base de conhecimento em memória para fins de demonstração.",
    version="0.1.0"
)

@app.get("/")
def root():
    """Redireciona para a documentação interativa."""
    return RedirectResponse(url="/docs")

# Mock knowledge base representing what would typically be in a Vector DB
KNOWLEDGE_BASE: List[Dict[str, Any]] = [
    {
        "id": 1,
        "title": "Cold Start no Cloud Run",
        "content": (
            "Cold start é o tempo de inicialização de uma instância serverless quando "
            "não há instâncias ativas. Pode levar de 200ms a 3s. Fatores que o aumentam: "
            "imagens Docker grandes, imports pesados como torch e tensorflow. "
            "Mitigação: min-instances, imagens leves, lazy loading."
        ),
        "tags": ["serverless", "cloud run", "cold start", "performance"],
    },
    {
        "id": 2,
        "title": "Microserviços vs Monólito",
        "content": (
            "Microserviços são unidades pequenas e independentes com uma única responsabilidade. "
            "Cada serviço é implantável, escalável e falha de forma isolada. "
            "Um monólito é mais simples para equipes pequenas e POCs, mas difícil de escalar "
            "partes individuais. Microserviços são ideais para produção com várias equipes."
        ),
        "tags": ["microserviços", "monólito", "arquitetura"],
    },
    {
        "id": 3,
        "title": "Gerenciamento de Segredos com GCP Secret Manager",
        "content": (
            "Segredos nunca devem existir no código ou na imagem Docker. "
            "O GCP Secret Manager armazena segredos versionados e auditados. "
            "O Cloud Run os injeta como variáveis de ambiente em tempo de execução via --set-secrets. "
            "Princípio do menor privilégio: cada microserviço acessa apenas os segredos necessários."
        ),
        "tags": ["segredos", "segurança", "gcp", "iam"],
    },
    {
        "id": 4,
        "title": "Pipeline vs Microserviços no MLOps",
        "content": (
            "Pipeline: sequencial e acoplado, ideal para ETL e treinamento de modelos. "
            "Microserviços: sob demanda e desacoplados, ideal para APIs e ferramentas de agentes. "
            "O treinamento de modelos usa pipelines. Servir o modelo como ferramenta de agente usa microserviços."
        ),
        "tags": ["pipeline", "mlops", "arquitetura", "agentes"],
    },
    {
        "id": 5,
        "title": "Agentes com Ferramentas como Microserviços",
        "content": (
            "Cada ferramenta de agente pode ser um microserviço independente no Cloud Run. "
            "Benefícios: observabilidade individual por ferramenta, escalabilidade independente, "
            "reutilização entre múltiplos agentes, isolamento de falhas, flexibilidade tecnológica. "
            "O agente Agno faz chamadas HTTP para os endpoints do microserviço."
        ),
        "tags": ["agentes", "ferramentas", "cloud run", "agno"],
    },
]

class SearchRequest(BaseModel):
    query: str
    top_k: int = 3

class FoundDocument(BaseModel):
    id: int
    title: str
    content: str
    tags: List[str]
    score: int

class SearchResponse(BaseModel):
    query: str
    total: int
    results: List[FoundDocument]

def search_by_relevance(query: str, top_k: int) -> List[Dict[str, Any]]:
    """
    Busca simples por palavra-chave (mock para busca semântica).
    """
    query_lower = query.lower()
    results = []

    for doc in KNOWLEDGE_BASE:
        score = 0
        for word in query_lower.split():
            if word in doc["title"].lower():
                score += 3
            if word in doc["content"].lower():
                score += 1
            if any(word in tag for tag in doc["tags"]):
                score += 2

        if score > 0:
            results.append({**doc, "score": score})

    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:top_k]

@app.post("/search", response_model=SearchResponse)
def search(req: SearchRequest) -> Any:
    """Endpoint para buscar documentos relevantes com base em uma consulta."""
    results = search_by_relevance(req.query, req.top_k)
    return {
        "query": req.query,
        "total": len(results),
        "results": results,
    }

@app.get("/health")
def health() -> Dict[str, str]:
    """Endpoint de verificação de saúde do microserviço."""
    return {"status": "ok", "service": "search-svc"}
