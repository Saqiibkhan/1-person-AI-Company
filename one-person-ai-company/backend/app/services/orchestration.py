"""
The real "Manager" of the system.

Per our Phase-1 architecture decision, this plain-Python module owns
the entire workflow: planning, dependency resolution, delegation,
the QA review loop, the max-revision limit, and human-approval
fallback. It calls into crews/agent_runner.py for exactly one LLM
call at a time and never hands control away to CrewAI itself.

Two distinct kinds of "failure" are handled here, and they are NOT
the same thing:
  - A technical/transient failure (the LLM call itself raises --
    network error, rate limit, malformed response that can't even be
    parsed) is retried automatically a bounded number of times
    (MAX_TASK_RETRIES) before the task is marked FAILED. This never
    touches revision_count.
  - A content rejection (QA reviewed real output and judged it
    doesn't meet requirements) goes through the existing revision
    loop (MAX_REVISIONS), which sends the actual feedback back to the
    agent -- that's a different, already-correct mechanism.
"""
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.enums import TaskStatus, ProjectStatus, EventType, can_transition
from app.models.project import Project
from app.models.task import Task
from app.models.agent_run import AgentRun
from app.models.review import Review
from app.schemas.task import TaskPlan
from app.schemas.review import QAReviewOutput
from app.crews.agent_runner import run_single_task
from app.crews.task_factory import (
    build_planning_prompt,
    build_execution_prompt,
    build_revision_prompt,
    build_qa_prompt,
    build_finalization_prompt,
)
from app.services.review_service import parse_qa_output
from app.services.memory_service import build_context_for_task
from app.services import event_service


def _set_task_status(db: Session, task: Task, status: TaskStatus) -> None:
    current = TaskStatus(task.status)
    if not can_transition(current, status):
        raise ValueError(f"Invalid task transition: {current} -> {status}")
    task.status = status.value
    db.commit()


# ---------------------------------------------------------------------------
# Planning (Section 9): the Manager decides what tasks are actually needed.
# ---------------------------------------------------------------------------
async def plan_project(db: Session, project: Project) -> list[Task]:
    project.status = ProjectStatus.PLANNING.value
    db.commit()
    await event_service.emit(db, project.id, EventType.PROJECT_STARTED.value, "Manager analyzing project objective")

    prompt, expected = build_planning_prompt(project.goal, project.description)
    raw = run_single_task("manager", prompt, expected)

    try:
        plan = TaskPlan.model_validate_json(_strip_fences(raw))
    except Exception:
        # One repair attempt: ask the manager again, but this time
        # only if the first parse truly failed (not on every call).
        repair_prompt = prompt + f"\n\nYour previous response could not be parsed as JSON. Return ONLY the JSON object."
        raw = run_single_task("manager", repair_prompt, expected)
        plan = TaskPlan.model_validate_json(_strip_fences(raw))

    title_to_id: dict[str, int] = {}
    created: list[Task] = []
    for item in plan.tasks:
        task = Task(
            project_id=project.id,
            title=item.title,
            description=item.description,
            requirements=item.requirements,
            assigned_agent=item.assigned_agent,
            status=TaskStatus.PENDING.value,
            depends_on=[],  # resolved in a second pass below
        )
        db.add(task)
        db.flush()  # get task.id without committing yet
        title_to_id[item.title] = task.id
        created.append(task)

    # Second pass: resolve dependency titles to real task ids now that
    # every task in this plan has an id.
    for item, task in zip(plan.tasks, created):
        task.depends_on = [title_to_id[t] for t in item.depends_on if t in title_to_id]

    db.commit()

    for task in created:
        await event_service.emit(
            db, project.id, EventType.TASK_CREATED.value,
            f"Manager created task: {task.title}", task_id=task.id,
        )

    await event_service.emit(
        db, project.id, EventType.AGENT_ASSIGNED.value,
        f"Manager created {len(created)} tasks",
    )
    return created


def _strip_fences(text: str) -> str:
    text = text.strip()
    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[len("json"):]
    return text.strip()


# ---------------------------------------------------------------------------
# QA review, with one JSON-repair retry (Phase-1 recommendation).
# ---------------------------------------------------------------------------
def _run_qa_review(task: Task, output: str) -> QAReviewOutput:
    prompt, expected = build_qa_prompt(task.title, task.description, task.requirements, output)
    raw = run_single_task("auditor", prompt, expected)
    try:
        return parse_qa_output(raw)
    except ValueError as first_error:
        repair_prompt = prompt + f"\n\nYour previous response was invalid: {first_error}. Return ONLY the JSON object, matching the schema exactly."
        raw = run_single_task("auditor", repair_prompt, expected)
        return parse_qa_output(raw)  # let this raise if it fails twice


# ---------------------------------------------------------------------------
# Execute a single ready task, including its QA loop.
# ---------------------------------------------------------------------------
async def execute_task(db: Session, task: Task) -> None:
    project_id = task.project_id
    _set_task_status(db, task, TaskStatus.RUNNING)
    task.started_at = datetime.now(timezone.utc)
    db.commit()

    context = build_context_for_task(db, task)
    is_revision = task.revision_count > 0

    await event_service.emit(
        db, project_id, EventType.TASK_STARTED.value,
        f"{task.assigned_agent.title()} Agent started: {task.title}", task_id=task.id,
    )

    if is_revision:
        last_review = (
            db.query(Review).filter(Review.task_id == task.id).order_by(Review.id.desc()).first()
        )
        prompt, expected = build_revision_prompt(
            task.title, task.description, task.requirements,
            task.output_data or "", last_review.issues if last_review else [],
            last_review.required_changes if last_review else [],
        )
    else:
        prompt, expected = build_execution_prompt(task.title, task.description, task.requirements, context)

    run = AgentRun(task_id=task.id, agent_name=task.assigned_agent, input=prompt)
    db.add(run)
    db.commit()
    db.refresh(run)

    # --- Agent execution, with automatic retry on technical failure ---
    max_attempts = 1 + settings.MAX_TASK_RETRIES
    output = None
    last_error: Exception | None = None
    for attempt in range(1, max_attempts + 1):
        try:
            output = run_single_task(task.assigned_agent, prompt, expected)
            break
        except Exception as exc:  # noqa: BLE001
            last_error = exc
            if attempt < max_attempts:
                await event_service.emit(
                    db, project_id, EventType.TASK_STARTED.value,
                    f"{task.assigned_agent.title()} Agent hit an error (attempt {attempt}/{max_attempts}) "
                    f"-- retrying automatically",
                    task_id=task.id,
                )

    if output is None:
        run.status = "FAILED"
        run.error = str(last_error)
        run.completed_at = datetime.now(timezone.utc)
        db.commit()
        _set_task_status(db, task, TaskStatus.FAILED)
        await event_service.emit(
            db, project_id, EventType.TASK_FAILED.value,
            f"{task.assigned_agent.title()} Agent failed after {max_attempts} attempt(s): {last_error}",
            task_id=task.id,
        )
        return

    run.output = output
    run.status = "COMPLETED"
    run.completed_at = datetime.now(timezone.utc)
    task.output_data = output
    db.commit()

    event_type = EventType.REVISION_SUBMITTED if is_revision else EventType.OUTPUT_SUBMITTED
    await event_service.emit(
        db, project_id, event_type.value,
        f"{task.assigned_agent.title()} Agent submitted output for: {task.title}", task_id=task.id,
    )

    # --- QA review ---
    _set_task_status(db, task, TaskStatus.REVIEWING)
    await event_service.emit(
        db, project_id, EventType.REVIEW_STARTED.value,
        f"QA/Auditor reviewing: {task.title}", task_id=task.id,
    )

    try:
        verdict = _run_qa_review(task, output)
    except Exception as exc:  # noqa: BLE001
        verdict = None
        last_qa_error = exc
        for attempt in range(2, max_attempts + 1):
            await event_service.emit(
                db, project_id, EventType.REVIEW_STARTED.value,
                f"QA/Auditor review attempt {attempt - 1}/{max_attempts - 1} failed -- retrying automatically",
                task_id=task.id,
            )
            try:
                verdict = _run_qa_review(task, output)
                break
            except Exception as retry_exc:  # noqa: BLE001
                last_qa_error = retry_exc

        if verdict is None:
            _set_task_status(db, task, TaskStatus.FAILED)
            await event_service.emit(
                db, project_id, EventType.TASK_FAILED.value,
                f"QA/Auditor could not produce a valid review after {max_attempts} attempt(s): {last_qa_error}",
                task_id=task.id,
            )
            return

    review = Review(
        task_id=task.id,
        agent_run_id=run.id,
        status=verdict.status,
        score=verdict.score,
        issues=verdict.issues,
        required_changes=verdict.required_changes,
        summary=verdict.summary,
    )
    db.add(review)
    db.commit()

    await event_service.emit(
        db, project_id, EventType.REVIEW_COMPLETED.value,
        f"QA/Auditor {verdict.status.replace('_', ' ')} \"{task.title}\" (score {verdict.score})",
        task_id=task.id, metadata={"score": verdict.score, "status": verdict.status},
    )

    if verdict.status == "approved":
        _set_task_status(db, task, TaskStatus.APPROVED)
        task.completed_at = datetime.now(timezone.utc)
        db.commit()
        await event_service.emit(
            db, project_id, EventType.TASK_APPROVED.value,
            f"\"{task.title}\" approved", task_id=task.id,
        )
        return

    # Rejected: revision loop with a hard cap (Section 6).
    task.revision_count += 1
    if task.revision_count <= settings.MAX_REVISIONS:
        _set_task_status(db, task, TaskStatus.REVISION_REQUIRED)
        db.commit()
        await event_service.emit(
            db, project_id, EventType.REVISION_REQUESTED.value,
            f"\"{task.title}\" sent back for revision ({task.revision_count}/{settings.MAX_REVISIONS})",
            task_id=task.id,
        )
        # execute_task() itself transitions REVISION_REQUIRED -> RUNNING
        # at its start; don't do it here too, or the second call to
        # execute_task sees an already-RUNNING task and rejects the
        # (invalid) RUNNING -> RUNNING transition.
        await execute_task(db, task)  # re-run immediately with feedback
    else:
        _set_task_status(db, task, TaskStatus.WAITING_FOR_HUMAN)
        db.commit()
        await event_service.emit(
            db, project_id, EventType.HUMAN_APPROVAL_REQUIRED.value,
            f"\"{task.title}\" failed QA after {settings.MAX_REVISIONS} revisions -- needs human attention",
            task_id=task.id,
        )


# ---------------------------------------------------------------------------
# Dependency resolution: which pending tasks are actually ready to run?
# ---------------------------------------------------------------------------
def get_ready_tasks(db: Session, project_id: int) -> list[Task]:
    all_tasks = db.query(Task).filter(Task.project_id == project_id).all()
    terminal_ok = {TaskStatus.APPROVED.value, TaskStatus.COMPLETED.value}
    ready = []
    for task in all_tasks:
        if task.status != TaskStatus.PENDING.value:
            continue
        deps = [t for t in all_tasks if t.id in (task.depends_on or [])]
        if all(d.status in terminal_ok for d in deps):
            ready.append(task)
    return ready


def project_is_blocked(db: Session, project_id: int) -> bool:
    tasks = db.query(Task).filter(Task.project_id == project_id).all()
    active = {TaskStatus.PENDING.value, TaskStatus.RUNNING.value, TaskStatus.REVIEWING.value, TaskStatus.REVISION_REQUIRED.value}
    waiting = any(t.status == TaskStatus.WAITING_FOR_HUMAN.value for t in tasks)
    nothing_active = not any(t.status in active for t in tasks)
    return waiting and nothing_active


def project_is_fully_approved(db: Session, project_id: int) -> bool:
    tasks = db.query(Task).filter(Task.project_id == project_id).all()
    if not tasks:
        return False
    return all(t.status in {TaskStatus.APPROVED.value, TaskStatus.COMPLETED.value} for t in tasks)


# ---------------------------------------------------------------------------
# Final deliverable assembly (Section 17/26).
# ---------------------------------------------------------------------------
async def finalize_project(db: Session, project: Project) -> None:
    tasks = db.query(Task).filter(Task.project_id == project.id).all()
    approved_work = [(t.title, t.output_data or "") for t in tasks]
    prompt, expected = build_finalization_prompt(project.goal, approved_work)
    final_output = run_single_task("manager", prompt, expected)

    from app.tools.file_tools import save_deliverable
    save_deliverable(project.id, "final_deliverable.md", final_output)

    project.status = ProjectStatus.COMPLETED.value
    db.commit()
    await event_service.emit(
        db, project.id, EventType.PROJECT_COMPLETED.value,
        "Manager produced the final company deliverable",
    )


# ---------------------------------------------------------------------------
# Main run loop, invoked as a FastAPI background task.
# ---------------------------------------------------------------------------
async def run_project(db: Session, project_id: int) -> None:
    project = db.query(Project).filter(Project.id == project_id).first()
    if project is None:
        return

    if not db.query(Task).filter(Task.project_id == project_id).first():
        await plan_project(db, project)

    project.status = ProjectStatus.RUNNING.value
    db.commit()

    while True:
        db.refresh(project)
        if project.status == ProjectStatus.CANCELLED.value:
            return

        ready = get_ready_tasks(db, project_id)
        if not ready:
            if project_is_fully_approved(db, project_id):
                await finalize_project(db, project)
                return
            if project_is_blocked(db, project_id):
                project.status = ProjectStatus.WAITING_FOR_HUMAN.value
                db.commit()
                await event_service.emit(
                    db, project_id, EventType.PROJECT_WAITING_FOR_HUMAN.value,
                    "Project is waiting for human review on one or more tasks",
                )
                return
            # Nothing ready and not blocked/complete -> genuinely stuck; stop safely.
            return

        for task in ready:
            await execute_task(db, task)
