"""
Runs exactly one agent on exactly one unit of work via CrewAI, and
returns plain text.

This is the ONLY place CrewAI's Agent/Task/Crew/Process objects get
touched. Per our Phase-1 architecture decision, CrewAI is a tool the
orchestrator calls for one task at a time -- it never owns the
overall workflow, revision loop, or human-approval logic. That logic
lives in services/orchestration.py in plain Python.

crewai itself is imported lazily inside run_single_task, not at
module load, so importing this module (e.g. from orchestration.py,
transitively from every API route) never requires crewai to be
installed unless an agent call actually happens.
"""
from app.agents.registry import AGENT_BUILDERS
from app.crews.llm_config import get_llm

_llm = None


def _get_shared_llm():
    global _llm
    if _llm is None:
        _llm = get_llm()
    return _llm


def run_single_task(agent_name: str, description: str, expected_output: str) -> str:
    """
    Build the named agent fresh, give it one CrewAI Task, run a
    single-agent sequential Crew, and return its raw text output.

    Raises whatever CrewAI/LiteLLM raises on failure -- the caller
    (orchestration.py) is responsible for catching this and marking
    the Task FAILED rather than crashing the whole project.
    """
    from crewai import Task as CrewTask, Crew, Process

    builder = AGENT_BUILDERS.get(agent_name)
    if builder is None:
        raise ValueError(f"Unknown agent: {agent_name}")

    agent = builder(_get_shared_llm())
    crew_task = CrewTask(description=description, expected_output=expected_output, agent=agent)
    crew = Crew(agents=[agent], tasks=[crew_task], process=Process.sequential, verbose=False)
    result = crew.kickoff()
    return str(result)
