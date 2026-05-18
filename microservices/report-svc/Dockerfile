FROM python:3.12-slim

# Copia o binário do uv diretamente da imagem oficial
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Variáveis para otimização do uv
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy

# Instala dependências
COPY pyproject.toml uv.lock* ./
RUN uv sync --frozen --no-install-project --no-dev

# Copia o código da aplicação
COPY main.py .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
