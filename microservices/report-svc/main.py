from typing import List, Dict, Any
from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime

app = FastAPI(
    title="Report Generator - Demo",
    description="Microservice responsible for receiving raw content and returning a Markdown formatted report.",
    version="0.1.0"
)

class DocumentInput(BaseModel):
    title: str
    content: str

class ReportRequest(BaseModel):
    report_title: str
    author: str
    documents: List[DocumentInput]
    additional_instructions: str = ""

class ReportResponse(BaseModel):
    title: str
    generated_at: str
    total_documents: int
    markdown: str
    characters: int

@app.post("/generate", response_model=ReportResponse)
def generate_report(req: ReportRequest) -> Any:
    """Generates a structured Markdown report from the received documents."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    lines = [
        f"# {req.report_title}",
        f"",
        f"**Author:** {req.author}  ",
        f"**Generated at:** {now}  ",
        f"**Total sources:** {len(req.documents)}",
        f"",
        "---",
        "",
        "## Executive Summary",
        "",
        f"This report consolidates {len(req.documents)} document(s) on the topic **{req.report_title}**.",
        "",
    ]

    if req.additional_instructions:
        lines += [
            "### Additional Context",
            "",
            req.additional_instructions,
            "",
        ]

    lines += ["## Analyzed Documents", ""]

    for i, doc in enumerate(req.documents, 1):
        lines += [
            f"### {i}. {doc.title}",
            "",
            doc.content,
            "",
        ]

    lines += [
        "---",
        "",
        "*Report generated automatically by report-svc*",
    ]

    markdown = "\n".join(lines)

    return {
        "title": req.report_title,
        "generated_at": now,
        "total_documents": len(req.documents),
        "markdown": markdown,
        "characters": len(markdown),
    }

@app.get("/health")
def health() -> Dict[str, str]:
    """Health check endpoint."""
    return {"status": "ok", "service": "report-svc"}
