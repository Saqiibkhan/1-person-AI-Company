"""
Builds the exact prompt text sent to CrewAI for each kind of call the
orchestrator makes: the Manager's decomposition, a worker agent's
task execution, a worker's revision, and the QA/Auditor's review.

Keeping these as plain string-builders (not buried inside
orchestration.py) makes the prompts easy to read, tune, and test
independently of the workflow logic.
"""
import json


def build_planning_prompt(goal: str, description: str | None) -> tuple[str, str]:
    description_line = f"\nAdditional context from the human owner: {description}" if description else ""
    prompt = f"""
Objective from the human owner:
{goal}
{description_line}

Decompose this objective into the smallest set of tasks actually needed
to deliver it. Only use these agent types: "researcher", "marketing", "builder".
Do not create a task for an agent type that isn't genuinely needed.

Respond with ONLY a JSON object (no markdown fences, no commentary) of this exact shape:

{{
  "tasks": [
    {{
      "title": "short task title",
      "description": "what the agent must actually do",
      "requirements": ["specific requirement 1", "specific requirement 2"],
      "assigned_agent": "researcher | marketing | builder",
      "depends_on": ["title of another task in this same list, if any"]
    }}
  ]
}}
""".strip()
    expected_output = "A single JSON object with a top-level 'tasks' array, matching the exact schema described."
    return prompt, expected_output


FILE_FORMAT_INSTRUCTIONS = """
If -- and only if -- your deliverable naturally consists of multiple
separate files (for example: source code, a multi-file configuration,
or several distinct documents), output EACH file wrapped exactly like
this, with a real relative path (folders allowed) and nothing else on
the marker lines:

===FILE: path/to/filename.ext===
<the complete file content>
===END FILE===

Repeat that block for every file. If your deliverable is a single
document or plan (the common case), just write it normally -- do NOT
wrap a single-document answer in these markers.
""".strip()


def build_execution_prompt(task_title: str, task_description: str, requirements: list[str], context: str) -> tuple[str, str]:
    req_lines = "\n".join(f"- {r}" for r in requirements) or "(none specified)"
    context_block = f"\nApproved context from prior work:\n{context}\n" if context else ""
    prompt = f"""
Task: {task_title}

Description:
{task_description}

Requirements:
{req_lines}
{context_block}
Produce your deliverable now. Be concrete and specific. Where you are
uncertain or making an assumption, label it clearly as an ASSUMPTION
rather than stating it as fact.

{FILE_FORMAT_INSTRUCTIONS}
""".strip()
    expected_output = "A complete, well-structured deliverable satisfying every listed requirement."
    return prompt, expected_output


def build_revision_prompt(
    task_title: str,
    task_description: str,
    requirements: list[str],
    previous_output: str,
    issues: list[str],
    required_changes: list[str],
) -> tuple[str, str]:
    req_lines = "\n".join(f"- {r}" for r in requirements) or "(none specified)"
    issues_lines = "\n".join(f"- {i}" for i in issues) or "(none listed)"
    changes_lines = "\n".join(f"- {c}" for c in required_changes) or "(none listed)"
    prompt = f"""
Task: {task_title}

Description:
{task_description}

Requirements:
{req_lines}

Your previous submission was reviewed by an independent QA auditor and
was NOT approved.

Your previous output:
{previous_output}

Issues found:
{issues_lines}

Required changes:
{changes_lines}

Revise your output to specifically address every issue and required
change above. Do not simply resubmit the same answer.

{FILE_FORMAT_INSTRUCTIONS}
""".strip()
    expected_output = "A revised deliverable that specifically addresses every listed issue and required change."
    return prompt, expected_output


def build_qa_prompt(task_title: str, task_description: str, requirements: list[str], agent_output: str) -> tuple[str, str]:
    req_lines = "\n".join(f"- {r}" for r in requirements) or "(none specified)"
    prompt = f"""
Original Task: {task_title}

Task Description:
{task_description}

Requirements:
{req_lines}

Agent Output (evaluate ONLY this -- you do not know who produced it or
what they believe about it):
{agent_output}

Evaluate this output strictly against the requirements above: requirement
satisfaction, completeness, relevance, accuracy, consistency, and evidence
where applicable.

Respond with ONLY a JSON object (no markdown fences, no commentary) of
this exact shape:

{json.dumps({
    "status": "approved | revision_required | failed",
    "score": "integer 0-100",
    "issues": ["specific issue found, if any"],
    "required_changes": ["specific, actionable change needed, if any"],
    "summary": "one or two sentence overall verdict",
}, indent=2)}
""".strip()
    expected_output = "A single JSON object matching the exact QA review schema described."
    return prompt, expected_output


def build_finalization_prompt(goal: str, approved_work: list[tuple[str, str]]) -> tuple[str, str]:
    sections = "\n\n".join(f"## {title}\n{output}" for title, output in approved_work)
    prompt = f"""
Original objective:
{goal}

All of the following pieces of work have been independently reviewed
and approved. Combine them into a single, coherent final deliverable
for the human owner. Do not simply concatenate them -- write a short
executive summary first, then organize the approved sections logically.

Approved work:
{sections}
""".strip()
    expected_output = "A single coherent final report combining all approved work, with an executive summary."
    return prompt, expected_output
