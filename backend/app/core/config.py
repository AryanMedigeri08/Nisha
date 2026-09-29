"""
Core configuration for PS26108 backend.
Loads settings from environment / .env file.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from project root
_PROJECT_ROOT = Path(__file__).resolve().parents[3]  # backend/app/core -> project root
_dotenv_path = _PROJECT_ROOT / ".env"
if _dotenv_path.exists():
    load_dotenv(_dotenv_path)

# -------------------------------------------------------------------
# Paths
# -------------------------------------------------------------------
PROJECT_ROOT = _PROJECT_ROOT
SEED_DATASET_PATH = PROJECT_ROOT / os.getenv("SEED_DATASET_PATH", "PS26108_Seed_Dataset_v1.xlsx")
PROCESSED_DIR = PROJECT_ROOT / os.getenv("PROCESSED_DIR", "data/processed")
SYNTHETIC_DIR = PROJECT_ROOT / os.getenv("SYNTHETIC_DIR", "data/synthetic")
EVALUATION_DIR = PROJECT_ROOT / os.getenv("EVALUATION_DIR", "data/evaluation")
EMBEDDINGS_DIR = PROJECT_ROOT / os.getenv("EMBEDDINGS_DIR", "data/embeddings")

# -------------------------------------------------------------------
# Database
# -------------------------------------------------------------------
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://ps26108_user:ps26108_pass@localhost:5432/ps26108_db",
)

# For Phase 1 (no PostgreSQL yet), we use SQLite as a local fallback.
SQLITE_URL = f"sqlite:///{PROJECT_ROOT / 'data' / 'ps26108_local.db'}"

# -------------------------------------------------------------------
# Embedding model
# -------------------------------------------------------------------
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
EMBEDDING_DIM = int(os.getenv("EMBEDDING_DIM", "384"))

# -------------------------------------------------------------------
# Reranker
# -------------------------------------------------------------------
RERANKER_MODEL = os.getenv("RERANKER_MODEL", "cross-encoder/ms-marco-MiniLM-L-6-v2")

# -------------------------------------------------------------------
# API
# -------------------------------------------------------------------
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8000"))
