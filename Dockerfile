# Dockerfile for sandboxed AI Engine
FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.cargo/bin:${PATH}"

COPY engine/ ./engine/
COPY shared/ ./shared/

WORKDIR /app/engine
RUN uv sync

EXPOSE 8000

# The engine can be run as a standalone API if needed, 
# but here it's prepared for the task-based execution.
CMD ["uv", "run", "phantom-engine"]
