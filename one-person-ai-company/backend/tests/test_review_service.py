import pytest

from app.services.review_service import parse_qa_output


def test_parses_clean_json():
    raw = '{"status": "approved", "score": 90, "issues": [], "required_changes": [], "summary": "Good."}'
    result = parse_qa_output(raw)
    assert result.status == "approved"
    assert result.score == 90


def test_strips_markdown_fences():
    raw = '```json\n{"status": "revision_required", "score": 40, "issues": ["missing data"], "required_changes": ["add data"], "summary": "Needs work."}\n```'
    result = parse_qa_output(raw)
    assert result.status == "revision_required"
    assert result.issues == ["missing data"]


def test_invalid_json_raises():
    with pytest.raises(ValueError):
        parse_qa_output("not json at all")


def test_invalid_schema_raises():
    # score out of range (must be 0-100)
    raw = '{"status": "approved", "score": 500, "issues": [], "required_changes": [], "summary": "x"}'
    with pytest.raises(ValueError):
        parse_qa_output(raw)
