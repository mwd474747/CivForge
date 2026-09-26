# CivForge Governance Kernel (8080) - minimal production container
# Governed artifact. Build: docker build -t civforge-kernel .
# Run: docker run -p 8080:8080 civforge-kernel
FROM python:3.11-slim

WORKDIR /app

# System deps (build if needed for some wheels)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy only what the kernel needs (core + backend + tools for CLI + receipts for persistence)
COPY frontend/ ./frontend/
COPY core/ ./core/
COPY backend/ ./backend/
COPY tools/ ./tools/
COPY receipts/ ./receipts/
COPY *.md SEPARATION.md AGENTS.md ./

# Persistence volume hint (SQLite + receipts live here)
VOLUME ["/app/receipts", "/app/gravity_backend.db"]

EXPOSE 8080

# Default: run the FastAPI kernel.
ENV PYTHONPATH=/app

CMD ["python", "-m", "uvicorn", "backend.sim_api:app", "--host", "0.0.0.0", "--port", "8080"]
