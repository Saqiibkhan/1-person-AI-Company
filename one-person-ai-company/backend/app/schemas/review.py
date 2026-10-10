from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class QAReviewOutput(BaseModel):
    """
    The QA/Auditor Agent's structured verdict (Section 5).
    Every QA call's raw text must validate against this model before
    it is trusted -- invalid JSON triggers a repair retry, never a
    silent pass-through.
    """
    status: Literal["approved", "revision_required", "failed"]
    score: int = Field(ge=0, le=100)
    issues: list[str] = []
    required_changes: list[str] = []
    summary: str


class ReviewOut(BaseModel):
    id: int
    task_id: int
    agent_run_id: int
    status: str
    score: int
    issues: list[str]
    required_changes: list[str]
    summary: str
    created_at: datetime

    class Config:
        from_attributes = True
