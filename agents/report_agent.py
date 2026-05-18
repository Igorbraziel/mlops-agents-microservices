import os
import httpx
from typing import List, Dict, Any
from agno.agent import Agent
from agno.models.google import Gemini
from agno.tools import tool

# Using a fallback to localhost for easier local testing
REPORT_SVC_URL = os.environ.get("REPORT_SVC_URL", "http://localhost:8002")

@tool(description=(
    "Generates a structured Markdown report from a list of documents. "
    "Use it when you need to consolidate researched information into a formatted document. "
    "Receives title, author, and a list of documents with title and content."
))
def generate_report(
    report_title: str,
    author: str,
    documents: List[Dict[str, str]],
    additional_instructions: str = "",
) -> Dict[str, Any]:
    """Calls the report generation microservice on Cloud Run."""
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
    name="Report Agent",
    model=Gemini(id="gemini-2.0-flash"),
    tools=[generate_report],
    instructions=[
        "You are an expert in creating clear and well-structured technical reports.",
        "When receiving documents to consolidate, use the generate_report tool.",
        "Always format the documents as a list of dictionaries with 'title' and 'content' keys.",
        "After generating the report, clearly display the 'markdown' field returned by the tool.",
    ],
    markdown=True,
)
