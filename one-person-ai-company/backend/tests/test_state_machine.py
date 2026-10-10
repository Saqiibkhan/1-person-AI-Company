from app.core.enums import TaskStatus, can_transition


def test_valid_transition_pending_to_running():
    assert can_transition(TaskStatus.PENDING, TaskStatus.RUNNING) is True


def test_invalid_transition_pending_to_completed():
    assert can_transition(TaskStatus.PENDING, TaskStatus.COMPLETED) is False


def test_completed_is_terminal():
    assert can_transition(TaskStatus.COMPLETED, TaskStatus.RUNNING) is False


def test_revision_required_can_go_to_waiting_for_human():
    assert can_transition(TaskStatus.REVISION_REQUIRED, TaskStatus.WAITING_FOR_HUMAN) is True
