"""
Parses and validates the QA/Auditor's raw text output against the
QAReviewOutput schema (Section 5), including a repair-retry when the
model returns malformed JSON -- so a formatting slip never gets
silently treated as either an approval or a crash.
"""
import json
import re

from pydantic import ValidationError

from app.schemas.review import QAReviewOutput


def _extract_json_block(text: str) -> str:
    """Strip markdown code fences if the model added them anyway."""
    match = re.search(r"\{.*\}", text, re.DOTALL)
    return match.group(0) if match else text


def parse_qa_output(raw_text: str) -> QAReviewOutput:
    """
    Raises ValueError if the text still doesn't validate. The caller
    (orchestration.py) is expected to call this once, and on failure
    re-run the auditor agent with the error appended, then call this
    again -- at most one repair attempt.
    """
    candidate = _extract_json_block(raw_text)
    try:
        data = json.loads(candidate)
    except json.JSONDecodeError as exc:
        raise ValueError(f"QA output was not valid JSON: {exc}") from exc

    try:
        return QAReviewOutput(**data)
    except ValidationError as exc:
        raise ValueError(f"QA output did not match the required schema: {exc}") from exc
