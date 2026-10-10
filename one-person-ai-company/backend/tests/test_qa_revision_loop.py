"""
The most important integration test (Section 35): simulates the full

    Agent -> Output -> QA -> REJECT -> Revision -> Agent -> Revised
    Output -> QA -> APPROVE -> Task Complete

cycle end-to-end through the real orchestration engine, with the LLM
call itself mocked out so this runs with no API key and no network
access -- it verifies OUR workflow logic, not the model's writing.
"""
import asyncio
import json

from app.core.enums import TaskStatus
from app.models.project import Project
from app.models.task import Task
from app.models.review import Review
from app.models.agent_run import AgentRun
from app.services import orchestration


def test_reject_then_approve_cycle(db_session, monkeypatch):
    project = Project(name="QA Loop Test", goal="Test the revision loop")
    db_session.add(project)
    db_session.commit()
    db_session.refresh(project)

    task = Task(
        project_id=project.id,
        title="Write a summary",
        description="Summarize the market",
        requirements=["Must mention at least two competitors"],
        assigned_agent="researcher",
        status=TaskStatus.PENDING.value,
        depends_on=[],
    )
    db_session.add(task)
    db_session.commit()
    db_session.refresh(task)

    # First call = the agent's initial (bad) output.
    # Second call = the QA rejection.
    # Third call = the agent's revised (good) output.
    # Fourth call = the QA approval.
    call_sequence = [
        "A summary with no competitors mentioned.",
        json.dumps({
            "status": "revision_required", "score": 40,
            "issues": ["No competitors mentioned"],
            "required_changes": ["Name at least two competitors"],
            "summary": "Missing required competitor analysis.",
        }),
        "A summary mentioning Competitor A and Competitor B.",
        json.dumps({
            "status": "approved", "score": 88, "issues": [],
            "required_changes": [], "summary": "Meets all requirements.",
        }),
    ]
    calls = {"n": 0}

    def fake_run_single_task(agent_name, prompt, expected_output):
        result = call_sequence[calls["n"]]
        calls["n"] += 1
        return result

    monkeypatch.setattr(orchestration, "run_single_task", fake_run_single_task)

    asyncio.run(orchestration.execute_task(db_session, task))

    db_session.refresh(task)
    assert task.status == TaskStatus.APPROVED.value
    assert task.revision_count == 1
    assert "Competitor A" in task.output_data

    reviews = db_session.query(Review).filter(Review.task_id == task.id).order_by(Review.id).all()
    assert len(reviews) == 2
    assert reviews[0].status == "revision_required"
    assert reviews[1].status == "approved"


def test_max_revisions_falls_back_to_human(db_session, monkeypatch):
    project = Project(name="Max Revisions Test", goal="Test the revision cap")
    db_session.add(project)
    db_session.commit()
    db_session.refresh(project)

    task = Task(
        project_id=project.id, title="Impossible task", description="Never satisfies QA",
        requirements=["Be perfect"], assigned_agent="builder",
        status=TaskStatus.PENDING.value, depends_on=[],
    )
    db_session.add(task)
    db_session.commit()
    db_session.refresh(task)

    rejection = json.dumps({
        "status": "revision_required", "score": 10, "issues": ["Still wrong"],
        "required_changes": ["Try again"], "summary": "Not good enough.",
    })

    def always_rejects(agent_name, prompt, expected_output):
        if agent_name == "auditor":
            return rejection
        return "An output that never satisfies QA."

    monkeypatch.setattr(orchestration, "run_single_task", always_rejects)

    asyncio.run(orchestration.execute_task(db_session, task))

    db_session.refresh(task)
    # MAX_REVISIONS defaults to 2 -> initial attempt + 2 revision
    # cycles = 3 total submissions, then it must stop retrying on its
    # own and wait for a human, never loop forever.
    assert task.status == TaskStatus.WAITING_FOR_HUMAN.value
    assert task.revision_count == 3


def test_transient_agent_error_recovers_via_automatic_retry(db_session, monkeypatch):
    """
    This is the exact bug the human owner reported: a technical hiccup
    (the agent call raising an exception -- network blip, rate limit,
    etc.) must NOT immediately end the task as permanently FAILED. It
    should retry automatically and, if a later attempt succeeds,
    proceed completely normally through QA and approval.
    """
    project = Project(name="Transient Error Test", goal="Recover from a flaky call")
    db_session.add(project)
    db_session.commit()
    db_session.refresh(project)

    task = Task(
        project_id=project.id, title="Build the API", description="desc",
        requirements=["Works"], assigned_agent="builder",
        status=TaskStatus.PENDING.value, depends_on=[],
    )
    db_session.add(task)
    db_session.commit()
    db_session.refresh(task)

    approval = json.dumps({
        "status": "approved", "score": 92, "issues": [],
        "required_changes": [], "summary": "Looks good.",
    })
    calls = {"n": 0}

    def flaky_then_recovers(agent_name, prompt, expected_output):
        calls["n"] += 1
        if agent_name == "builder" and calls["n"] == 1:
            raise RuntimeError("simulated transient network error")
        if agent_name == "builder":
            return "A complete, working implementation."
        return approval

    monkeypatch.setattr(orchestration, "run_single_task", flaky_then_recovers)

    asyncio.run(orchestration.execute_task(db_session, task))

    db_session.refresh(task)
    assert task.status == TaskStatus.APPROVED.value
    assert task.output_data == "A complete, working implementation."
    # This was a technical retry, not a content revision -- must not
    # be counted against the QA revision budget.
    assert task.revision_count == 0

    runs = db_session.query(AgentRun).filter(AgentRun.task_id == task.id).all()
    assert len(runs) == 1
    assert runs[0].status == "COMPLETED"


def test_technical_failure_still_ends_as_failed_after_exhausting_retries(db_session, monkeypatch):
    """The retry budget must still be bounded -- persistent technical
    failure (every attempt raises) must not retry forever."""
    project = Project(name="Persistent Error Test", goal="A call that never recovers")
    db_session.add(project)
    db_session.commit()
    db_session.refresh(project)

    task = Task(
        project_id=project.id, title="Broken task", description="desc",
        requirements=[], assigned_agent="builder",
        status=TaskStatus.PENDING.value, depends_on=[],
    )
    db_session.add(task)
    db_session.commit()
    db_session.refresh(task)

    def always_raises(agent_name, prompt, expected_output):
        raise RuntimeError("simulated permanent network outage")

    monkeypatch.setattr(orchestration, "run_single_task", always_raises)

    asyncio.run(orchestration.execute_task(db_session, task))

    db_session.refresh(task)
    assert task.status == TaskStatus.FAILED.value

    runs = db_session.query(AgentRun).filter(AgentRun.task_id == task.id).all()
    assert len(runs) == 1
    assert runs[0].status == "FAILED"
    assert "simulated permanent network outage" in runs[0].error
