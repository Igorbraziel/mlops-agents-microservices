import os
import httpx
from typing import Dict, Any
from agno.agent import Agent
from agno.models.google import Gemini
from agno.tools import tool

# Using a fallback to localhost for easier local testing without strictly enforcing the env var presence
SEARCH_SVC_URL = os.environ.get("SEARCH_SVC_URL", "http://localhost:8001")

@tool(description=(
    "Searches for relevant documents in the knowledge base about MLOps, "
    "serverless, microservices, and agents. Use it when you need technical "
    "information about these topics. Returns a list of documents with title and content."
))
def search_documents(query: str, top_k: int = 3) -> Dict[str, Any]:
    """Calls the semantic search microservice on Cloud Run."""
    response = httpx.post(
        f"{SEARCH_SVC_URL}/search",
        json={"query": query, "top_k": top_k},
        timeout=15.0,
    )
    response.raise_for_status()
    return response.json()

search_agent = Agent(
    name="Search Agent",
    model=Gemini(id="gemini-2.0-flash"),
    tools=[search_documents],
    instructions=[
        "You are an expert in technical research regarding MLOps and AI architectures.",
        "When receiving a question, use the search_documents tool to find relevant information.",
        "Return the results in a structured way: list the found documents with title and summary.",
        "Always indicate how many documents were found.",
    ],
    markdown=True,
)
