"""
Single source of truth mapping an agent name (as stored on Task.assigned_agent)
to its builder function and to the human-readable info shown on the
Workforce page (Section 18 of the frontend spec).
"""
from app.agents.manager import build_manager_agent
from app.agents.researcher import build_researcher_agent
from app.agents.marketing import build_marketing_agent
from app.agents.builder import build_builder_agent
from app.agents.auditor import build_auditor_agent

AGENT_BUILDERS = {
    "manager": build_manager_agent,
    "researcher": build_researcher_agent,
    "marketing": build_marketing_agent,
    "builder": build_builder_agent,
    "auditor": build_auditor_agent,
}

AGENT_INFO = {
    "manager": {
        "role": "Company coordination and task delegation",
        "description": "Understands the objective, plans tasks, and coordinates the workforce.",
        "capabilities": ["planning", "delegation", "dependency management", "coordination"],
    },
    "researcher": {
        "role": "Research and information gathering",
        "description": "Gathers and analyzes information, producing structured, sourced research.",
        "capabilities": ["web research", "source gathering", "market research", "fact checking"],
    },
    "marketing": {
        "role": "Business and market strategy",
        "description": "Converts research into practical marketing and business strategy.",
        "capabilities": ["competitor analysis", "customer analysis", "positioning", "go-to-market strategy"],
    },
    "builder": {
        "role": "Creating practical deliverables",
        "description": "Produces concrete deliverables: plans, specs, documents, or code.",
        "capabilities": ["technical plans", "specifications", "documentation", "code"],
    },
    "auditor": {
        "role": "Independent quality control",
        "description": "Independently reviews every deliverable against its task requirements.",
        "capabilities": ["requirement validation", "accuracy checks", "completeness", "consistency"],
    },
}
