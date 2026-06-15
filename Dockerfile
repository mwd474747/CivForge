# CivForge Governance Kernel (8080) - minimal production container
# Governed artifact. Build: docker build -t civforge-kernel .
# Run: docker run -p 8080:8080 --env NEXUS_URL=http://host.docker.internal:8082 civforge-kernel
FROM python:3.11-slim

WORKDIR /app

# System deps (build if needed for some wheels)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy only what the kernel needs (core + backend + tools for CLI/poller + receipts for persistence)
COPY frontend/ ./frontend/
COPY core/ ./core/
COPY backend/ ./backend/
COPY tools/ ./tools/
COPY receipts/ ./receipts/
COPY *.md SEPARATION.md AGENTS.md .grok/ ./

# Persistence volume hint (SQLite + receipts live here)
VOLUME ["/app/receipts", "/app/gravity_backend.db"]

EXPOSE 8080

# Default: run the FastAPI kernel (override for poller: python -m tools.nexus_command_poller --loop)
ENV PYTHONPATH=/app
ENV NEXUS_URL=http://127.0.0.1:8082

CMD ["python", "-m", "uvicorn", "backend.sim_api:app", "--host", "0.0.0.0", "--port", "8080"]
