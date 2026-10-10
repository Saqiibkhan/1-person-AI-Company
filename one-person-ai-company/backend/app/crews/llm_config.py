"""
Builds the LLM object CrewAI agents use, based on env-configured
provider (Section 14). Nothing else in the codebase imports a
provider SDK directly -- this is the one place that knows about
OpenRouter vs Ollama.

The crewai import is deferred to call-time (not module load) so the
rest of the app -- CRUD endpoints, orchestration logic, tests -- never
pays the cost of importing crewai unless an agent is actually run.
"""
from app.core.config import settings


def get_llm():
    from crewai import LLM

    if settings.LLM_PROVIDER == "ollama":
        return LLM(model=f"ollama/{settings.OLLAMA_MODEL}", base_url="http://localhost:11434")

    # Default: OpenRouter. CrewAI (via LiteLLM) supports OpenRouter
    # natively with the "openrouter/<model>" prefix; it reads
    # OPENROUTER_API_KEY from the environment automatically.
    import os

    os.environ.setdefault("OPENROUTER_API_KEY", settings.OPENROUTER_API_KEY)
    return LLM(model=f"openrouter/{settings.MODEL_NAME}")
