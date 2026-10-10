from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models.agent_run import AgentRun

router = APIRouter(prefix="/runs", tags=["runs"])


@router.get("/{run_id}")
def get_run(run_id: int, db: Session = Depends(get_db)):
    run = db.query(AgentRun).filter(AgentRun.id == run_id).first()
    if not run:
        raise HTTPException(404, "Agent run not found")
    return {
        "id": run.id, "task_id": run.task_id, "agent_name": run.agent_name,
        "status": run.status, "input": run.input, "output": run.output,
        "error": run.error, "started_at": run.started_at, "completed_at": run.completed_at,
    }
