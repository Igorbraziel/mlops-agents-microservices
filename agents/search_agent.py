import os
import httpx
from typing import Dict, Any
from agno.agent import Agent
from agno.models.google import Gemini
from agno.tools import tool

# Using a fallback to localhost for easier local testing without strictly enforcing the env var presence
SEARCH_SVC_URL = os.environ.get("SEARCH_SVC_URL", "http://localhost:8001")

@tool(description=(
    "Busca documentos relevantes na base de conhecimento sobre MLOps, "
    "serverless, microserviços e agentes. Use quando precisar de informações "
    "técnicas sobre esses tópicos. Retorna uma lista de documentos com título e conteúdo."
))
def search_documents(query: str, top_k: int = 3) -> Dict[str, Any]:
    """Faz a chamada para o microserviço de busca semântica no Cloud Run."""
    response = httpx.post(
        f"{SEARCH_SVC_URL}/search",
        json={"query": query, "top_k": top_k},
        timeout=15.0,
    )
    response.raise_for_status()
    return response.json()

search_agent = Agent(
    name="search_agent",
    description="Agente especialista em pesquisa técnica sobre MLOps e arquiteturas de IA.",
    model=Gemini(id="gemini-2.5-flash-lite"),
    fallback_models=[
        Gemini(id="gemini-3.1-flash-lite-preview"),
        Gemini(id="gemini-2.5-flash"),
        Gemini(id="gemini-2.0-flash"),
        Gemini(id="gemma-3-27b-it"),
        Gemini(id="gemma3:12b"),
        Gemini(id="gemma3:4b"),
        Gemini(id="gemma3:1b"),
    ],
    tools=[search_documents],
    instructions=[
        "Você é um especialista em pesquisa técnica sobre MLOps e arquiteturas de IA.",
        "Ao receber uma pergunta, use a ferramenta search_documents para encontrar informações relevantes.",
        "Retorne os resultados de forma estruturada: liste os documentos encontrados com título e resumo.",
        "Sempre indique quantos documentos foram encontrados.",
    ],
    markdown=True,
)
