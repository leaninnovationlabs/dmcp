FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS builder

WORKDIR /app

RUN apt-get update && apt-get install -y \
    --no-install-recommends \
    build-essential \
    pkg-config \
    libpq-dev \
    default-libmysqlclient-dev \
    && rm -rf /var/lib/apt/lists/*

RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    uv sync --locked --no-install-project

COPY . .

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-editable --compile-bytecode

FROM python:3.12-slim-bookworm

WORKDIR /app

RUN apt-get update && apt-get install -y \
    --no-install-recommends \
    libpq5 \
    libmariadb3 \
    && rm -rf /var/lib/apt/lists/* \
    && groupadd -r -g 1000 appuser \
    && useradd -r -g appuser -u 1000 -m -d /app -s /bin/bash appuser

COPY --from=builder --chown=appuser:appuser /app/.venv /app/.venv
COPY --from=builder --chown=appuser:appuser /app/main.py /app/alembic.ini ./
COPY --from=builder --chown=appuser:appuser /app/app ./app
COPY --from=builder --chown=appuser:appuser /app/alembic ./alembic
COPY --from=builder --chown=appuser:appuser /app/frontend ./frontend

ENV PATH="/app/.venv/bin:$PATH"

# Set default values for host and port
ENV HOST=0.0.0.0
ENV PORT=8000

USER appuser

# Use environment variable for EXPOSE
EXPOSE ${PORT}

# Use environment variables for host and port in CMD
CMD ["sh", "-c", "alembic upgrade head && uvicorn main:app --host ${HOST} --port ${PORT}"]