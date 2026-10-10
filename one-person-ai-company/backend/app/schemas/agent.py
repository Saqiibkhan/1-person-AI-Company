from pydantic import BaseModel


class AgentInfo(BaseModel):
    name: str
    role: str
    description: str
    capabilities: list[str]


class AgentStatsOut(BaseModel):
    name: str
    total_runs: int
    approved_count: int
    revision_count: int
    failed_count: int
