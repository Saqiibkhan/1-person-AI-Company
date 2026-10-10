"""
Entry point for the One-Person AI Company backend.

Wires together the database, CORS, and every API router. All actual
logic lives in api/*.py (HTTP boundary) and services/orchestration.py
(the real workflow engine) -- this file only assembles them.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.database.connection import init_db
from app.api import projects, tasks, agents, runs, websocket

app = FastAPI(
    title="One-Person AI Company",
    description="An AI-powered operating system for a one-person company.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_ORIGIN, "http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup() -> None:
    init_db()


@app.get("/health")
def health_check() -> dict:
    return {"status": "ok", "service": "one-person-ai-company-backend"}


app.include_router(projects.router)
app.include_router(tasks.router)
app.include_router(agents.router)
app.include_router(runs.router)
app.include_router(websocket.router)
