"""
Database engine and session management.

Defaults to a local SQLite file so the project runs with zero external
services. Set DATABASE_URL in .env to point at PostgreSQL instead
(e.g. postgresql://postgres:postgres@localhost:5432/ai_company) --
nothing else in the codebase needs to change, since all access goes
through SQLAlchemy's ORM.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.database.base import Base

connect_args = {"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(settings.DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db() -> None:
    """Create all tables. Called once at app startup."""
    # Import models here (not at module top) so they register on Base
    # before create_all runs, without creating a circular import.
    from app.models import project, task, agent_run, review, event  # noqa: F401

    Base.metadata.create_all(bind=engine)


def get_db():
    """FastAPI dependency that yields a DB session and always closes it."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
