# PS26108 — Production Deployment & Hosting Guide

This guide documents how to build, run, test, and host the **PS26108 AI-Powered Indian Standards Recommendation Engine (Phase 7)** in both local development and containerized production environments.

---

## 1. System Requirements

- **Operating System:** Linux (Ubuntu 22.04+ recommended), macOS, or Windows 10/11 with WSL2.
- **Python:** Python 3.10, 3.11, or 3.12 (venv recommended).
- **Node.js:** Node.js v18+ and npm v9+ (for frontend).
- **Memory (RAM):** Minimum 4 GB RAM (8 GB recommended for caching neural embedding & reranking models).
- **Disk Space:** 5 GB free disk space.
- **Optional:** NVIDIA GPU with CUDA support for accelerated batch inference (CPU fallback is automatically supported).

---

## 2. Environment Configuration

1. Copy the example environment template:
   ```bash
   cp .env.example .env
   ```
2. Configure required parameters in `.env`:
   - `DATABASE_URL`: PostgreSQL connection string (or defaults to SQLite `data/ps26108_local.db`).
   - `EMBEDDING_MODEL`: `all-MiniLM-L6-v2`
   - `RERANKER_MODEL`: `cross-encoder/ms-marco-MiniLM-L-6-v2`
   - `API_PORT`: `8000`

---

## 3. Local Development Setup

### Backend Setup

1. Create and activate a Python virtual environment:
   ```bash
   python -m venv .venv
   # Windows:
   .venv\Scripts\activate
   # Linux/macOS:
   source .venv/bin/activate
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Ingest the seed dataset (Scheme-1 BIS Standards & QCO Orders):
   ```bash
   python scripts/ingest_seed.py
   ```
4. Build the Knowledge Graph and retrieval index:
   ```bash
   python scripts/build_knowledge_graph.py
   python scripts/build_retrieval_index.py
   ```
5. Launch the backend API server:
   ```bash
   uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

### Frontend Setup

1. In a separate terminal, navigate to `frontend/`:
   ```bash
   cd frontend
   npm install
   ```
2. Start the Vite development server:
   ```bash
   npm run dev
   ```
3. Open `http://localhost:3000` in your browser. (The Vite server proxies `/api` and `/health` requests to `http://localhost:8000`).

---

## 4. Single-Port Production Build

In production, FastAPI directly serves the pre-built React single page application from `frontend/dist`.

1. Build the frontend bundle:
   ```bash
   cd frontend
   npm run build
   cd ..
   ```
2. Start the unified production server:
   ```bash
   uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --workers 2
   ```
3. Access the entire application at `http://localhost:8000`.

---

## 5. Docker & Container Deployment

### Using Docker Compose (Recommended)

1. Ensure Docker and Docker Compose are running.
2. Build and launch the multi-container stack:
   ```bash
   docker-compose up --build -d
   ```
3. Check container status:
   ```bash
   docker-compose ps
   ```
4. Verify backend health probe:
   ```bash
   curl http://localhost:8000/health
   curl http://localhost:8000/health/ready
   ```
5. Access the application in your browser at `http://localhost:8000`.

---

## 6. Verification and Health Probes

- **Liveness Probe:** `GET /health` returns `{ "status": "healthy", "service": "PS26108 Standards Recommendation Engine" }`
- **Readiness Probe:** `GET /health/ready` validates database connectivity and model caching.
- **OpenAPI Interactive Documentation:** `GET /docs` and `GET /redoc`

---

## 7. Running Tests and Verification Suites

Run the complete regression suite (all 134+ tests across Phases 1–7):
```bash
pytest tests/unit/ -v
```

Run Phase 7 review workflow evaluation:
```bash
python scripts/evaluate_review_workflow.py
```

Run Phase 7 integrity audit:
```bash
python scripts/review_integrity.py
```
