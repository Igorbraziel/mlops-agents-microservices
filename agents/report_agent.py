import os
import httpx
from typing import List, Dict, Any
from agno.agent import Agent
from agno.models.google import Gemini
from agno.tools import tool

# Using a fallback to localhost for easier local testing
REPORT_SVC_URL = os.environ.get("REPORT_SVC_URL", "http://localhost:8002")

@tool(description=(
    "Gera um relatório estruturado em Markdown a partir de uma lista de documentos. "
    "Use quando precisar consolidar informações pesquisadas em um documento formatado. "
    "Recebe título, autor e uma lista de documentos com título e conteúdo."
))
def generate_report(
    report_title: str,
    author: str,
    documents: List[Dict[str, str]],
    additional_instructions: str = "",
) -> Dict[str, Any]:
    """Faz a chamada para o microserviço de geração de relatórios no Cloud Run."""
    response = httpx.post(
        f"{REPORT_SVC_URL}/generate",
        json={
            "report_title": report_title,
            "author": author,
            "documents": documents,
            "additional_instructions": additional_instructions,
        },
        timeout=15.0,
    )
    response.raise_for_status()
    return response.json()

report_agent = Agent(
    name="Agente de Relatórios",
    model=Gemini(id="gemini-2.5-flash-lite"),
    fallback_models=[
        Gemini(id="gemini-3.1-flash-lite"),
        Gemini(id="gemini-2.5-flash"),
        Gemini(id="gemma-4-31b"),
    ],
    tools=[generate_report],
    instructions=[
        "Você é um especialista em criar relatórios técnicos claros e bem estruturados.",
        "Ao receber documentos para consolidar, use a ferramenta generate_report.",
        "Sempre formate os documentos como uma lista de dicionários com as chaves 'title' e 'content'.",
        "Após gerar o relatório, exiba claramente o campo 'markdown' retornado pela ferramenta.",
    ],
    markdown=True,
)
