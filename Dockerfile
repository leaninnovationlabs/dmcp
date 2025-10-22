FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS builder

WORKDIR /app

RUN apt-get update && apt-get install -y \
    --no-install-recommends \
    build-essential \
    pkg-config \
    curl \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js latest version
RUN curl -fsSL https://deb.nodesource.com/setup_22.x | bash - \
    && apt-get install -y nodejs

RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    uv sync --locked --no-install-project

COPY . .

# Build React frontend
WORKDIR /app/frontend
RUN npm ci && npm run build
RUN rm -rf /app/frontend

# Back to app root
WORKDIR /app

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
COPY --from=builder --chown=appuser:appuser /app/public /app/public

# Create data directory for SQLite database in case of SQLite database
RUN mkdir -p /app/data && chown appuser:appuser /app/data

ENV PATH="/app/.venv/bin:$PATH"

# Set default values for host and port
ENV HOST=0.0.0.0
ENV PORT=8000

USER appuser

# Use environment variable for EXPOSE
EXPOSE ${PORT}

# Use environment variables for host and port in CMD
CMD ["sh", "-c", "alembic upgrade head && uvicorn main:app --host ${HOST} --port ${PORT}"]