from typing import List, Dict, Any
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from datetime import datetime

app = FastAPI(
    title="Gerador de Relatórios - Demo",
    description="Microserviço responsável por receber conteúdo bruto e retornar um relatório formatado em Markdown.",
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

@app.get("/")
def root():
    """Redireciona para a documentação interativa."""
    return RedirectResponse(url="/docs")

@app.post("/generate", response_model=ReportResponse)
def generate_report(req: ReportRequest) -> Any:
    """Gera um relatório estruturado em Markdown a partir dos documentos recebidos."""
    now = datetime.now().strftime("%d/%m/%Y %H:%M")

    lines = [
        f"# {req.report_title}",
        f"",
        f"**Autor:** {req.author}  ",
        f"**Gerado em:** {now}  ",
        f"**Total de fontes:** {len(req.documents)}",
        f"",
        "---",
        "",
        "## Resumo Executivo",
        "",
        f"Este relatório consolida {len(req.documents)} documento(s) sobre o tópico **{req.report_title}**.",
        "",
    ]

    if req.additional_instructions:
        lines += [
            "### Contexto Adicional",
            "",
            req.additional_instructions,
            "",
        ]

    lines += ["## Documentos Analisados", ""]

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
        "*Relatório gerado automaticamente por report-svc*",
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
