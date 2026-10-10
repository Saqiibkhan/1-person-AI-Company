"""Basic CRUD tests using a real in-process app + isolated DB, no LLM calls involved."""
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database.connection import get_db
from app.database.base import Base
from app.models import project, task, agent_run, review, event  # noqa: F401

# StaticPool keeps every connection sharing the SAME in-memory SQLite
# DB across threads. Without it, TestClient's request thread would see
# a brand-new (empty) in-memory database and every query would 404.
engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(bind=engine)
Base.metadata.create_all(bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


def test_health():
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_create_and_get_project():
    resp = client.post("/projects", json={"name": "Test Co", "goal": "Launch a test product"})
    assert resp.status_code == 201
    project_id = resp.json()["id"]
    assert resp.json()["status"] == "CREATED"

    resp = client.get(f"/projects/{project_id}")
    assert resp.status_code == 200
    assert resp.json()["name"] == "Test Co"


def test_stop_project():
    resp = client.post("/projects", json={"name": "To Stop", "goal": "Something"})
    project_id = resp.json()["id"]
    resp = client.post(f"/projects/{project_id}/stop")
    assert resp.status_code == 200
    assert resp.json()["status"] == "CANCELLED"


def test_get_nonexistent_project_404():
    resp = client.get("/projects/999999")
    assert resp.status_code == 404


def test_task_files_and_download_endpoints():
    import zipfile
    import io as _io
    from app.database.connection import SessionLocal as _UnusedRealSessionLocal  # noqa: F401
    from app.models.task import Task as TaskModel
    from app.core.enums import TaskStatus as TS

    resp = client.post("/projects", json={"name": "File Export Test", "goal": "Build something"})
    project_id = resp.json()["id"]

    db = TestingSessionLocal()
    task = TaskModel(
        project_id=project_id,
        title="Build the API",
        description="desc",
        requirements=[],
        assigned_agent="builder",
        status=TS.APPROVED.value,
        depends_on=[],
        output_data=(
            "===FILE: app/main.py===\nprint('hi')\n===END FILE===\n\n"
            "===FILE: README.md===\n# Hello\n===END FILE==="
        ),
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    task_id = task.id
    db.close()

    resp = client.get(f"/tasks/{task_id}/files")
    assert resp.status_code == 200
    paths = {f["path"] for f in resp.json()["files"]}
    assert paths == {"app/main.py", "README.md"}

    resp = client.get(f"/tasks/{task_id}/download")
    assert resp.status_code == 200
    assert resp.headers["content-type"] == "application/zip"
    with zipfile.ZipFile(_io.BytesIO(resp.content)) as zf:
        names = zf.namelist()
        assert any(n.endswith("app/main.py") for n in names)
        assert any(n.endswith("README.md") for n in names)
