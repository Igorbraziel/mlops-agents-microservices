import os
from dotenv import load_dotenv

# Load .env in local development
load_dotenv()

from agno.agent import Agent
from agno.models.google import Gemini
from agno.team import Team

from search_agent import search_agent
from report_agent import report_agent

# ── Orchestrator as a Team in Agno ──────────────────────────────────────────
# The Team coordinates multiple agents: decides who to call and in what order.
orchestrator = Team(
    name="MLOps Orchestrator",
    mode="coordinate",  # the orchestrator decides who does what
    model=Gemini(id="gemini-2.0-flash"),
    members=[search_agent, report_agent],
    instructions=[
        "You coordinate two specialized agents:",
        "- 'Search Agent': searches technical information in the knowledge base",
        "- 'Report Agent': generates structured reports from information",
        "",
        "Standard flow for report requests:",
        "1. Call the Search Agent to search for relevant documents.",
        "2. Pass the results to the Report Agent to generate the report.",
        "3. Present the final report to the user.",
        "",
        "For simple questions that don't need a report, use only the Search Agent.",
    ],
    markdown=True,
)

# ── Usage examples ──────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("\n" + "="*60)
    print("DEMO 1: Simple search (search_agent only)")
    print("="*60)
    orchestrator.print_response(
        "What are microservices and what is the difference compared to a pipeline?",
        stream=True,
    )

    print("\n" + "="*60)
    print("DEMO 2: Search + Report (both agents)")
    print("="*60)
    orchestrator.print_response(
        "Research about secrets security and cold starts, "
        "then generate a report named 'Best Practices in Production' with what you find. "
        "Author: MLOps Group",
        stream=True,
    )
