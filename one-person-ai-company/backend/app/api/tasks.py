import re

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.database.connection import get_db, SessionLocal
from app.models.task import Task
from app.models.review import Review
from app.models.agent_run import AgentRun
from app.schemas.task import TaskOut, TaskOutputOut, TaskFilesOut
from app.schemas.review import ReviewOut
from app.core.enums import TaskStatus
from app.services import event_service, orchestration
from app.tools.file_tools import parse_files_from_output, build_zip

router = APIRouter(prefix="/tasks", tags=["tasks"])


def _fallback_filename(task: Task) -> str:
    """A safe single-file name to use when an agent's output has no
    ===FILE:=== markers -- i.e. it's one document, not a file set."""
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", task.title.strip().lower()).strip("-")
    return f"{slug or f'task-{task.id}'}.md"


def _get_task_or_404(task_id: int, db: Session) -> Task:
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(404, "Task not found")
    return task


@router.get("/{task_id}", response_model=TaskOut)
def get_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(404, "Task not found")
    return task


@router.get("/{task_id}/output", response_model=TaskOutputOut)
def get_task_output(task_id: int, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(404, "Task not found")
    return TaskOutputOut(task_id=task.id, output=task.output_data, revision_count=task.revision_count)


@router.get("/{task_id}/files", response_model=TaskFilesOut)
def get_task_files(task_id: int, db: Session = Depends(get_db)):
    """
    Section: file/folder deliverables. Parses the task's latest output
    into real (path, content) files -- either the multiple files an
    agent explicitly produced (e.g. source code), or a single document
    as one file, so the frontend always has something concrete to list
    and download instead of one undifferentiated blob of text.
    """
    task = _get_task_or_404(task_id, db)
    if not task.output_data:
        return TaskFilesOut(task_id=task.id, files=[])

    files = parse_files_from_output(task.output_data, _fallback_filename(task))
    return TaskFilesOut(task_id=task.id, files=[{"path": p, "content": c} for p, c in files])


@router.get("/{task_id}/download")
def download_task_files(task_id: int, db: Session = Depends(get_db)):
    """Zips this task's parsed files and returns them as a download."""
    task = _get_task_or_404(task_id, db)
    if not task.output_data:
        raise HTTPException(409, "This task has no output yet")

    files = parse_files_from_output(task.output_data, _fallback_filename(task))
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", task.title.strip().lower()).strip("-") or f"task-{task.id}"

    zip_bytes = build_zip(files, root_folder=slug)
    return Response(
        content=zip_bytes,
        media_type="application/zip",
        headers={"Content-Disposition": f'attachment; filename="{slug}.zip"'},
    )


@router.get("/{task_id}/review", response_model=ReviewOut | None)
def get_latest_review(task_id: int, db: Session = Depends(get_db)):
    review = (
        db.query(Review).filter(Review.task_id == task_id).order_by(Review.id.desc()).first()
    )
    return review


@router.get("/{task_id}/history")
def get_task_history(task_id: int, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(404, "Task not found")
    runs = db.query(AgentRun).filter(AgentRun.task_id == task_id).order_by(AgentRun.id).all()
    reviews = db.query(Review).filter(Review.task_id == task_id).order_by(Review.id).all()
    return {
        "task_id": task_id,
        "runs": [
            {"id": r.id, "agent_name": r.agent_name, "status": r.status, "output": r.output,
             "error": r.error, "started_at": r.started_at, "completed_at": r.completed_at}
            for r in runs
        ],
        "reviews": [
            {"id": r.id, "status": r.status, "score": r.score, "issues": r.issues,
             "required_changes": r.required_changes, "summary": r.summary, "created_at": r.created_at}
            for r in reviews
        ],
    }


@router.post("/{task_id}/approve", response_model=TaskOut)
def approve_task(task_id: int, db: Session = Depends(get_db)):
    """Human manually approves a task stuck in WAITING_FOR_HUMAN (Section 10)."""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(404, "Task not found")
    if task.status != TaskStatus.WAITING_FOR_HUMAN.value:
        raise HTTPException(409, "Task is not waiting for human approval")
    task.status = TaskStatus.APPROVED.value
    db.commit()
    db.refresh(task)
    return task


@router.post("/{task_id}/reject", response_model=TaskOut)
def reject_task(task_id: int, db: Session = Depends(get_db)):
    """Human rejects a task outright; it stays WAITING_FOR_HUMAN for manual handling."""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(404, "Task not found")
    task.status = TaskStatus.CANCELLED.value
    db.commit()
    db.refresh(task)
    return task


@router.post("/{task_id}/retry", status_code=202)
def retry_task(task_id: int, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """Resets a task to PENDING (fresh revision count) and resumes the project run."""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(404, "Task not found")
    task.revision_count = 0
    task.status = TaskStatus.PENDING.value
    db.commit()

    def _resume():
        import asyncio
        resume_db = SessionLocal()
        try:
            asyncio.run(orchestration.run_project(resume_db, task.project_id))
        finally:
            resume_db.close()

    background_tasks.add_task(_resume)
    return {"message": "Task reset and project run resumed"}
