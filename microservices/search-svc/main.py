from typing import List, Dict, Any
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(
    title="Semantic Search - Demo",
    description="Search microservice using an in-memory knowledge base for demonstration purposes.",
    version="0.1.0"
)

# Mock knowledge base representing what would typically be in a Vector DB
KNOWLEDGE_BASE: List[Dict[str, Any]] = [
    {
        "id": 1,
        "title": "Cold Start in Cloud Run",
        "content": (
            "Cold start is the initialization time of a serverless instance when "
            "there are no active instances. It can take from 200ms to 3s. Factors that increase it: "
            "large Docker images, heavy imports like torch and tensorflow. "
            "Mitigation: min-instances, lightweight images, lazy loading."
        ),
        "tags": ["serverless", "cloud run", "cold start", "performance"],
    },
    {
        "id": 2,
        "title": "Microservices vs Monolith",
        "content": (
            "Microservices are small, independent units with a single responsibility. "
            "Each service is deployable, scalable, and fails in isolation. "
            "A monolith is simpler for small teams and POCs, but harder to scale "
            "individual parts. Microservices are ideal for production with multiple teams."
        ),
        "tags": ["microservices", "monolith", "architecture"],
    },
    {
        "id": 3,
        "title": "Secrets Management with GCP Secret Manager",
        "content": (
            "Secrets must never exist in the code or the Docker image. "
            "GCP Secret Manager stores versioned and audited secrets. "
            "Cloud Run injects them as environment variables at runtime via --set-secrets. "
            "Principle of least privilege: each microservice accesses only the secrets it needs."
        ),
        "tags": ["secrets", "security", "gcp", "iam"],
    },
    {
        "id": 4,
        "title": "Pipeline vs Microservices in MLOps",
        "content": (
            "Pipeline: sequential and coupled, ideal for ETL and model training. "
            "Microservices: on-demand and decoupled, ideal for APIs and agent tools. "
            "Model training uses pipelines. Serving the model as an agent tool uses microservices."
        ),
        "tags": ["pipeline", "mlops", "architecture", "agents"],
    },
    {
        "id": 5,
        "title": "Agents with Tools as Microservices",
        "content": (
            "Each agent tool can be an independent microservice in Cloud Run. "
            "Benefits: individual observability per tool, independent scaling, "
            "reuse across multiple agents, fault isolation, technological flexibility. "
            "The Agno agent makes HTTP calls to the microservice endpoints."
        ),
        "tags": ["agents", "tools", "cloud run", "agno"],
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
    Simple keyword search (mock for semantic search).
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
    """Endpoint to search relevant documents based on a query."""
    results = search_by_relevance(req.query, req.top_k)
    return {
        "query": req.query,
        "total": len(results),
        "results": results,
    }

@app.get("/health")
def health() -> Dict[str, str]:
    """Health check endpoint of the microservice."""
    return {"status": "ok", "service": "search-svc"}
