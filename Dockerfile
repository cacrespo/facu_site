# Usar la imagen oficial de Astral uv con Python slim
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

WORKDIR /app

# Compilar bytecode para arranques más rápidos
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy
ENV PYTHONUNBUFFERED=1

# Instalar dependencias usando el lockfile
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-install-project --no-dev

# Agregar el entorno virtual de uv al PATH
ENV PATH="/app/.venv/bin:$PATH"

# Copiar el código de la aplicación
COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
