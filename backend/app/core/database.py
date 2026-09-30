"""
SQLAlchemy database session setup.
Phase 1: Uses SQLite. Phase 6+: Will switch to PostgreSQL via DATABASE_URL.
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

from backend.app.core.config import SQLITE_URL

def _normalize_db_url(url: str) -> str:
    """Normalize PostgreSQL URL to explicitly use psycopg2 dialect for SQLAlchemy."""
    url = url.strip()
    if url.startswith("postgresql+psycopg2://"):
        return url
    if url.startswith("postgresql+psycopg://"):
        return url.replace("postgresql+psycopg://", "postgresql+psycopg2://", 1)
    if url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql+psycopg2://", 1)
    if url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgresql+psycopg2://", 1)
    return url


raw_db_url = os.getenv("DATABASE_URL")
if raw_db_url and raw_db_url.strip():
    DB_URL = _normalize_db_url(raw_db_url)
    engine = create_engine(DB_URL, echo=False, future=True, pool_pre_ping=True)
else:
    DB_URL = SQLITE_URL
    engine = create_engine(DB_URL, echo=False, future=True, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    """Declarative base for all ORM models."""
    pass


def init_db():
    """Create all tables. Idempotent."""
    Base.metadata.create_all(bind=engine)


def get_db():
    """FastAPI dependency – yields a DB session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
