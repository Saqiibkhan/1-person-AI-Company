from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database.connection import get_db
from app.models.agent_run import AgentRun
from app.models.review import Review
from app.schemas.agent import AgentInfo, AgentStatsOut
from app.agents.registry import AGENT_INFO

router = APIRouter(prefix="/agents", tags=["agents"])


@router.get("", response_model=list[AgentInfo])
def list_agents():
    return [
        AgentInfo(name=name, role=info["role"], description=info["description"], capabilities=info["capabilities"])
        for name, info in AGENT_INFO.items()
    ]


@router.get("/{agent_name}/stats", response_model=AgentStatsOut)
def get_agent_stats(agent_name: str, db: Session = Depends(get_db)):
    total = db.query(AgentRun).filter(AgentRun.agent_name == agent_name).count()
    failed = db.query(AgentRun).filter(AgentRun.agent_name == agent_name, AgentRun.status == "FAILED").count()

    run_ids = [r.id for r in db.query(AgentRun.id).filter(AgentRun.agent_name == agent_name).all()]
    approved = db.query(Review).filter(Review.agent_run_id.in_(run_ids), Review.status == "approved").count() if run_ids else 0
    revisions = db.query(Review).filter(Review.agent_run_id.in_(run_ids), Review.status == "revision_required").count() if run_ids else 0

    return AgentStatsOut(name=agent_name, total_runs=total, approved_count=approved, revision_count=revisions, failed_count=failed)
