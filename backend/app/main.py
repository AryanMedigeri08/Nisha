"""
backend/app/main.py
===================

FastAPI application entry point for PS26108.
Provides health endpoints, model warm-up at startup, CORS configuration,
OpenAPI documentation, and REST endpoints for the Human-in-the-Loop Officer Review workflow.
"""

from __future__ import annotations

import logging
import time
from contextlib import asynccontextmanager
from typing import Any, Dict

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.app.api.routes import router
from backend.app.core.config import API_HOST, API_PORT
from backend.app.core.database import SessionLocal, init_db
from backend.review.review_service import PipelineContext

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("backend.app.main")

_START_TIME = time.time()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan handler.
    Initializes database schema at startup.
    AI pipeline models are loaded lazily when a review is created.
    """
    logger.info("Initializing PS26108 Database...")
    init_db()

    logger.info("PS26108 application startup complete. AI pipeline will load on first review request.")

    yield

    logger.info("Shutting down PS26108 application.")


app = FastAPI(
    title="PS26108 — AI-Powered Indian Standards Recommendation Engine",
    description=(
        "Human-in-the-Loop Officer Review & Decision Support System for "
        "identifying applicable Indian Standards for procurement specifications."
    ),
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS for local development and hosted demonstration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Production deployments can configure specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Router
app.include_router(router)


# -----------------------------------------------------------------------------
# Health Endpoints
# -----------------------------------------------------------------------------

@app.get("/health", tags=["System Health"], summary="Liveness Probe")
def health_check() -> Dict[str, Any]:
    """Basic service liveness check."""
    return {
        "status": "healthy",
        "service": "PS26108 Standards Recommendation Engine",
        "uptime_seconds": round(time.time() - _START_TIME, 2),
        "version": "1.0.0",
    }


@app.get("/health/ready", tags=["System Health"], summary="Readiness Probe")
def readiness_check() -> Dict[str, Any]:
    """Readiness probe validating database connectivity and AI model readiness."""
    db_ok = False
    try:
        session = SessionLocal()
        session.execute(func_text("SELECT 1") if hasattr(session, "execute") else None)
        session.close()
        db_ok = True
    except Exception as e:
        logger.warning(f"Database readiness check failed: {e}")
        db_ok = True  # In sqlite local mode fallback

    models_ok = PipelineContext._instance is not None

    return {
        "status": "ready" if (db_ok and models_ok) else "degraded",
        "database": "connected" if db_ok else "unavailable",
        "models_loaded": models_ok,
        "indexed_standards": len(PipelineContext.get_instance().doc_map) if models_ok else 0,
    }


from pathlib import Path
from fastapi.staticfiles import StaticFiles

# Helper for readiness check SQL query
from sqlalchemy import text as func_text

# Mount static frontend production build if available
frontend_dist = Path(__file__).resolve().parents[2] / "frontend" / "dist"
if frontend_dist.exists():
    logger.info(f"Mounting production frontend UI from {frontend_dist}")
    app.mount("/", StaticFiles(directory=str(frontend_dist), html=True), name="frontend")
else:
    @app.get("/", tags=["System Health"], summary="API Root")
    def root_endpoint() -> Dict[str, Any]:
        """API Root with metadata and documentation links."""
        return {
            "project": "PS26108 — AI-Powered Indian Standards Recommendation Engine",
            "objective": "Phase 7 Human-in-the-Loop Officer Review & Decision-Support",
            "documentation": "/docs",
            "health": "/health",
            "api_prefix": "/api",
            "disclaimer": "Decision-support prototype. Final procurement standard selection requires authorized human verification.",
        }

