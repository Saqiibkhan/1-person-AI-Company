from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class ProjectCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    goal: str = Field(..., min_length=1)


class ProjectOut(BaseModel):
    id: int
    name: str
    description: Optional[str]
    goal: str
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
