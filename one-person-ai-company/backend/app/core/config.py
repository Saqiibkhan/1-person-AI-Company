"""
Centralized application settings, loaded from environment variables.

Nothing here is hard-coded. See ../.env.example for the full list of
variables this reads.
"""
import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    # --- LLM provider (Section 14) ---
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "openrouter")
    OPENROUTER_API_KEY: str = os.getenv("OPENROUTER_API_KEY", "")
    MODEL_NAME: str = os.getenv("MODEL_NAME", "openai/gpt-4o-mini")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "llama3")

    # --- Database ---
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./ai_company.db")

    # --- Revision control (Section 6): QA content rejections ---
    MAX_REVISIONS: int = int(os.getenv("MAX_REVISIONS", "2"))

    # --- Technical retry control (Section 27): transient failures --
    # network errors, malformed/unparseable LLM responses -- get
    # retried automatically this many times before a task is marked
    # FAILED. Separate from MAX_REVISIONS, which governs QA content
    # rejections, not plumbing failures.
    MAX_TASK_RETRIES: int = int(os.getenv("MAX_TASK_RETRIES", "2"))

    # --- CORS ---
    FRONTEND_ORIGIN: str = os.getenv("FRONTEND_ORIGIN", "http://localhost:5173")


settings = Settings()
