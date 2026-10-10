"""
Project-level "company memory" (Section 11).

For the MVP this is intentionally simple: approved task outputs
already live in Task.output_data, so "memory" here just means
building the *relevant slice* of that to hand to the next agent --
never the entire project history (Section 29: cost control).
"""
from sqlalchemy.orm import Session

from app.models.task import Task
from app.core.enums import TaskStatus


def build_context_for_task(db: Session, task: Task) -> str:
    """
    Returns the concatenated approved output of this task's direct
    dependencies only -- not the whole project's history.
    """
    if not task.depends_on:
        return ""

    dependency_tasks = (
        db.query(Task)
        .filter(Task.id.in_(task.depends_on))
        .filter(Task.status.in_([TaskStatus.APPROVED.value, TaskStatus.COMPLETED.value]))
        .all()
    )
    sections = []
    for dep in dependency_tasks:
        sections.append(f"### {dep.title}\n{dep.output_data or ''}")
    return "\n\n".join(sections)
