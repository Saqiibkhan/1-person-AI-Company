from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class TaskOut(BaseModel):
    id: int
    project_id: int
    title: str
    description: str
    requirements: list[str]
    assigned_agent: str
    status: str
    priority: str
    depends_on: list[int]
    revision_count: int
    created_at: datetime
    updated_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True


class TaskOutputOut(BaseModel):
    task_id: int
    output: Optional[str]
    revision_count: int


class TaskFile(BaseModel):
    """One file parsed out of an agent's output (see tools/file_tools.py)."""
    path: str
    content: str


class TaskFilesOut(BaseModel):
    task_id: int
    files: list[TaskFile]


class TaskPlanItem(BaseModel):
    """
    One item of the Manager Agent's task decomposition (Section 9).
    The Manager's raw JSON output is validated against a list of these
    before any Task rows are created -- an invalid plan never reaches
    the database.
    """
    title: str
    description: str
    requirements: list[str] = []
    assigned_agent: str  # "researcher" | "marketing" | "builder"
    depends_on: list[str] = []  # titles of other tasks in this same plan


class TaskPlan(BaseModel):
    tasks: list[TaskPlanItem]
