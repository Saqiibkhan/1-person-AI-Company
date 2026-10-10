from datetime import datetime, timezone

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship

from app.database.base import Base


class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False)
    agent_run_id = Column(Integer, ForeignKey("agent_runs.id"), nullable=False)

    status = Column(String(30), nullable=False)  # approved | revision_required | failed
    score = Column(Integer, nullable=False, default=0)
    issues = Column(JSON, nullable=False, default=list)
    required_changes = Column(JSON, nullable=False, default=list)
    summary = Column(Text, nullable=False, default="")

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    task = relationship("Task", back_populates="reviews")
