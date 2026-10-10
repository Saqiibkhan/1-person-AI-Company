"""
Shared pytest fixtures.

Uses an isolated in-memory SQLite database per test so tests never
touch the developer's real ai_company.db file, and never require a
running Postgres instance.
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database.base import Base
# Import models so they register on Base.metadata before create_all.
from app.models import project, task, agent_run, review, event  # noqa: F401


@pytest.fixture()
def db_session():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
