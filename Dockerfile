# ====================================================================
# PS26108 Production Dockerfile (Render Backend Deployment)
# Python 3.11 FastAPI backend with CPU-only PyTorch & ML inference
# ====================================================================

FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

WORKDIR /app

# Install minimal OS dependencies for network & builds
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install CPU-only PyTorch first to avoid CUDA/NVIDIA GPU bloat
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu

# Install Python requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application backend, scripts, seed dataset, and indexes
COPY backend/ /app/backend/
COPY scripts/ /app/scripts/
COPY PS26108_Seed_Dataset_v1.xlsx /app/
COPY data/ /app/data/

# Render sets the PORT environment variable dynamically (defaults to 8000)
EXPOSE 8000

# Health check probe
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:${PORT:-8000}/health || exit 1

# Launch production FastAPI server on Render's dynamic PORT
CMD ["sh", "-c", "uvicorn backend.app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
