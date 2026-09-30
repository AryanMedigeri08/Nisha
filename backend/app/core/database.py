"""
SQLAlchemy database session setup.
Phase 1: Uses SQLite. Phase 6+: Will switch to PostgreSQL via DATABASE_URL.
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

from backend.app.core.config import SQLITE_URL

raw_db_url = os.getenv("DATABASE_URL")
if raw_db_url:
    # Render PostgreSQL URLs may start with postgres://; SQLAlchemy requires postgresql://
    if raw_db_url.startswith("postgres://"):
        DB_URL = raw_db_url.replace("postgres://", "postgresql://", 1)
    else:
        DB_URL = raw_db_url
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
