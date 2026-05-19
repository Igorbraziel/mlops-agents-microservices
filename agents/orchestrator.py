import os
from dotenv import load_dotenv, find_dotenv, dotenv_values

# Load .env in local development. Use find_dotenv() so we locate a .env
# file up the directory tree (repo root) when running from subfolders.
dotenv_path = find_dotenv()
if dotenv_path:
    load_dotenv(dotenv_path)
else:
    # fallback: let load_dotenv try the current working directory
    load_dotenv()

from agno.models.google import Gemini
from agno.team import Team

from search_agent import search_agent
from report_agent import report_agent

# ── Orchestrator as a Team in Agno ──────────────────────────────────────────
# The Team coordinates multiple agents: decides who to call and in what order.
orchestrator = Team(
    name="Orquestrador MLOps",
    mode="coordinate",  # the orchestrator decides who does what
    model=Gemini(id="gemini-2.5-flash-lite"),
    fallback_models=[
        Gemini(id="gemini-3.1-flash-lite"),
        Gemini(id="gemini-2.5-flash"),
        Gemini(id="gemma-4-31b"),
    ],
    members=[search_agent, report_agent],
    instructions=[
        "Você coordena dois agentes especializados:",
        "- 'Agente de Busca': busca informações técnicas na base de conhecimento.",
        "- 'Agente de Relatórios': gera relatórios estruturados a partir das informações.",
        "",
        "Fluxo padrão para solicitações de relatório:",
        "1. Chame o Agente de Busca para pesquisar documentos relevantes.",
        "2. Passe os resultados para o Agente de Relatórios para gerar o relatório.",
        "3. Apresente o relatório final ao usuário.",
        "",
        "Para perguntas simples que não precisam de um relatório, use apenas o Agente de Busca.",
    ],
    markdown=True,
)

# ── Usage examples ──────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("\n" + "="*60)
    print("DEMO 1: Busca simples (apenas search_agent)")
    print("="*60)
    orchestrator.print_response(
        "O que são microserviços e qual a diferença em relação a um pipeline?",
        stream=True,
    )

    print("\n" + "="*60)
    print("DEMO 2: Busca + Relatório (ambos os agentes)")
    print("="*60)
    orchestrator.print_response(
        "Pesquise sobre segurança de segredos e cold starts, "
        "depois gere um relatório chamado 'Boas Práticas em Produção' com o que encontrar. "
        "Autor: Grupo MLOps",
        stream=True,
    )
