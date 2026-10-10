"""
Shared status enums (Section 18 and Agent status list).

Kept as plain str-Enums (not SQLAlchemy Enum types) so SQLite and
PostgreSQL both store them as plain strings without extra setup, and
so Pydantic schemas can reuse the exact same enum.
"""
from enum import Enum


class ProjectStatus(str, Enum):
    CREATED = "CREATED"
    PLANNING = "PLANNING"
    RUNNING = "RUNNING"
    WAITING_FOR_HUMAN = "WAITING_FOR_HUMAN"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class TaskStatus(str, Enum):
    PENDING = "PENDING"
    PLANNING = "PLANNING"
    WAITING_FOR_DEPENDENCY = "WAITING_FOR_DEPENDENCY"
    RUNNING = "RUNNING"
    REVIEWING = "REVIEWING"
    REVISION_REQUIRED = "REVISION_REQUIRED"
    APPROVED = "APPROVED"
    FAILED = "FAILED"
    WAITING_FOR_HUMAN = "WAITING_FOR_HUMAN"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class AgentStatus(str, Enum):
    IDLE = "IDLE"
    WORKING = "WORKING"
    REVIEWING = "REVIEWING"
    REVISING = "REVISING"
    WAITING = "WAITING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class ReviewStatus(str, Enum):
    APPROVED = "approved"
    REVISION_REQUIRED = "revision_required"
    FAILED = "failed"


class EventType(str, Enum):
    PROJECT_CREATED = "PROJECT_CREATED"
    PROJECT_STARTED = "PROJECT_STARTED"
    PROJECT_COMPLETED = "PROJECT_COMPLETED"
    PROJECT_STOPPED = "PROJECT_STOPPED"
    PROJECT_WAITING_FOR_HUMAN = "PROJECT_WAITING_FOR_HUMAN"
    TASK_CREATED = "TASK_CREATED"
    TASK_STARTED = "TASK_STARTED"
    AGENT_ASSIGNED = "AGENT_ASSIGNED"
    OUTPUT_SUBMITTED = "OUTPUT_SUBMITTED"
    REVIEW_STARTED = "REVIEW_STARTED"
    REVIEW_COMPLETED = "REVIEW_COMPLETED"
    REVISION_REQUESTED = "REVISION_REQUESTED"
    REVISION_SUBMITTED = "REVISION_SUBMITTED"
    TASK_APPROVED = "TASK_APPROVED"
    TASK_FAILED = "TASK_FAILED"
    HUMAN_APPROVAL_REQUIRED = "HUMAN_APPROVAL_REQUIRED"


# --- Section 18: explicit, enforced state transition table ---
# Checked in one place (services/orchestration.py) so invalid jumps
# (e.g. PENDING -> COMPLETED) can never happen silently.
ALLOWED_TASK_TRANSITIONS: dict[TaskStatus, set[TaskStatus]] = {
    TaskStatus.PENDING: {TaskStatus.WAITING_FOR_DEPENDENCY, TaskStatus.RUNNING, TaskStatus.CANCELLED},
    TaskStatus.WAITING_FOR_DEPENDENCY: {TaskStatus.RUNNING, TaskStatus.CANCELLED},
    TaskStatus.RUNNING: {TaskStatus.REVIEWING, TaskStatus.FAILED, TaskStatus.CANCELLED},
    TaskStatus.REVIEWING: {TaskStatus.APPROVED, TaskStatus.REVISION_REQUIRED, TaskStatus.FAILED, TaskStatus.WAITING_FOR_HUMAN},
    TaskStatus.REVISION_REQUIRED: {TaskStatus.RUNNING, TaskStatus.WAITING_FOR_HUMAN, TaskStatus.CANCELLED},
    TaskStatus.WAITING_FOR_HUMAN: {TaskStatus.APPROVED, TaskStatus.RUNNING, TaskStatus.CANCELLED},
    TaskStatus.APPROVED: {TaskStatus.COMPLETED},
    TaskStatus.FAILED: {TaskStatus.RUNNING, TaskStatus.CANCELLED},
    TaskStatus.COMPLETED: set(),
    TaskStatus.CANCELLED: set(),
    TaskStatus.PLANNING: {TaskStatus.PENDING},
}


def can_transition(current: TaskStatus, target: TaskStatus) -> bool:
    return target in ALLOWED_TASK_TRANSITIONS.get(current, set())
