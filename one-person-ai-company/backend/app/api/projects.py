import re

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.database.connection import get_db, SessionLocal
from app.models.project import Project
from app.models.task import Task
from app.models.event import Event
from app.schemas.project import ProjectCreate, ProjectOut
from app.schemas.task import TaskOut
from app.schemas.event import EventOut
from app.core.enums import ProjectStatus, EventType, TaskStatus
from app.services import orchestration, event_service
from app.tools.file_tools import parse_files_from_output, build_zip, OUTPUT_DIR

router = APIRouter(prefix="/projects", tags=["projects"])


@router.post("", response_model=ProjectOut, status_code=201)
def create_project(payload: ProjectCreate, db: Session = Depends(get_db)):
    project = Project(
        name=payload.name,
        description=payload.description,
        goal=payload.goal,
        status=ProjectStatus.CREATED.value,
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


@router.get("", response_model=list[ProjectOut])
def list_projects(db: Session = Depends(get_db)):
    return db.query(Project).order_by(Project.created_at.desc()).all()


@router.get("/{project_id}", response_model=ProjectOut)
def get_project(project_id: int, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(404, "Project not found")
    return project


def _run_in_background(project_id: int) -> None:
    """
    Runs in a fresh DB session, since the request-scoped session from
    get_db() closes as soon as the endpoint returns.
    """
    import asyncio

    db = SessionLocal()
    try:
        asyncio.run(orchestration.run_project(db, project_id))
    finally:
        db.close()


@router.post("/{project_id}/run", status_code=202)
def run_project(project_id: int, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(404, "Project not found")
    if project.status == ProjectStatus.RUNNING.value:
        raise HTTPException(409, "Project is already running")

    background_tasks.add_task(_run_in_background, project_id)
    return {"message": "Project execution started", "project_id": project_id}


@router.post("/{project_id}/stop", response_model=ProjectOut)
def stop_project(project_id: int, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(404, "Project not found")
    project.status = ProjectStatus.CANCELLED.value
    db.commit()
    db.refresh(project)
    return project


@router.get("/{project_id}/tasks", response_model=list[TaskOut])
def get_project_tasks(project_id: int, db: Session = Depends(get_db)):
    return db.query(Task).filter(Task.project_id == project_id).order_by(Task.id).all()


@router.get("/{project_id}/events", response_model=list[EventOut])
def get_project_events(project_id: int, db: Session = Depends(get_db)):
    return db.query(Event).filter(Event.project_id == project_id).order_by(Event.created_at).all()


@router.get("/{project_id}/download")
def download_project_deliverable(project_id: int, db: Session = Depends(get_db)):
    """
    Zips every approved task's files into one folder-structured archive
    (tasks/<task-title>/...), plus the combined final_deliverable.md the
    Manager wrote in finalize_project, if the project has completed.
    This is the actual "files within folders, with a download option"
    the human owner gets for a finished project.
    """
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(404, "Project not found")

    tasks = (
        db.query(Task)
        .filter(Task.project_id == project_id)
        .filter(Task.status.in_([TaskStatus.APPROVED.value, TaskStatus.COMPLETED.value]))
        .all()
    )
    if not tasks:
        raise HTTPException(409, "This project has no approved deliverables yet")

    all_files: list[tuple[str, str]] = []
    for task in tasks:
        if not task.output_data:
            continue
        slug = re.sub(r"[^a-zA-Z0-9]+", "-", task.title.strip().lower()).strip("-") or f"task-{task.id}"
        fallback_name = f"{slug}.md"
        for path, content in parse_files_from_output(task.output_data, fallback_name):
            all_files.append((f"tasks/{slug}/{path}", content))

    import os
    final_path = os.path.join(OUTPUT_DIR, str(project_id), "final_deliverable.md")
    if os.path.exists(final_path):
        with open(final_path, encoding="utf-8") as f:
            all_files.append(("final_deliverable.md", f.read()))

    project_slug = re.sub(r"[^a-zA-Z0-9]+", "-", project.name.strip().lower()).strip("-") or f"project-{project_id}"
    zip_bytes = build_zip(all_files, root_folder=project_slug)
    return Response(
        content=zip_bytes,
        media_type="application/zip",
        headers={"Content-Disposition": f'attachment; filename="{project_slug}.zip"'},
    )
