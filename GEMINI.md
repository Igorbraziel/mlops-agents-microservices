# Project Context: MLOps Agents Microservices

## Project Overview
This is a Python-based software project designed to demonstrate a multi-agent architecture utilizing shared microservices. The project leverages **Agno** for orchestrating AI agents and **FastAPI** for exposing agent tools as independent microservices. The architecture is designed for deployment on Google Cloud Run, showcasing independent scaling, isolated observability, and reusable infrastructure.

**Main Technologies:**
- Python (>=3.12)
- `uv` (Ultra-fast Python package installer and resolver)
- `FastAPI` & `uvicorn` (For microservices)
- `agno` (For AI agent orchestration)
- Google Cloud Run & Secret Manager (Deployment and Security)

## Building and Running

### Dependency Management
This project strictly uses `uv` for dependency management.
- **Initialize/Add dependencies:** `uv add <package>`
- **Sync environment:** `uv sync`
- **Run applications:** `uv run main.py` or `uv run uvicorn main:app --reload`

### Running the Project
- The main entry point for the global project is `main.py`, executable via `uv run main.py`.
- For individual microservices (e.g., `search-svc`, `report-svc` as described in the docs), navigate to their respective directories and run the FastAPI server:
  ```bash
  uv run uvicorn main:app --host 0.0.0.0 --port 8080 --reload
  ```

### Deployment
Microservices are containerized using Docker. The standard build process utilizes `uv` to install dependencies in the system environment optimized for Docker:
```dockerfile
# Inside Dockerfile
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy
COPY pyproject.toml uv.lock* ./
RUN uv sync --frozen --no-install-project --no-dev
```
Deployments are typically orchestrated via CLI scripts (e.g., `deploy.sh`) targeting Google Cloud Run.

## Development Conventions
- **Tooling:** Always use `pyproject.toml` instead of `requirements.txt`.
- **Architecture:** Keep agent tools decoupled as independent microservices. This allows for isolated observability and independent scaling.
- **Security:** Never commit secrets (e.g., API keys) to version control. Use `.env` for local development and GCP Secret Manager for production.
- **Agents:** Use `agno.agent.Agent` and `agno.team.Team` to orchestrate multi-agent workflows.

For more detailed implementation guidelines and architectural diagrams, refer to `docs/guia-implementacao-demo.md`.