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
This project strictly uses `uv` for dependency management for Python and `npm` for the frontend.
- **Python:** `uv sync`
- **Frontend:** `cd frontend && npm install`

### Running the Project
The project consists of three main parts:

1. **Microservices (Search & Report):**
   ```bash
   cd microservices/search-svc && uv run uvicorn main:app --port 8081
   cd microservices/report-svc && uv run uvicorn main:app --port 8082
   ```

2. **Orchestrator API:**
   ```bash
   cd agents && uv run python api.py
   ```

3. **React Frontend:**
   ```bash
   cd frontend && npm run dev
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