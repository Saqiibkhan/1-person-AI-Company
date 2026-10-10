from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class EventOut(BaseModel):
    id: int
    project_id: int
    task_id: Optional[int]
    event_type: str
    message: str
    event_metadata: Optional[dict] = None
    created_at: datetime

    class Config:
        from_attributes = True
