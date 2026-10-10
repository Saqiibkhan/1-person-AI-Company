# One-Person AI Company

An AI-powered operating system for a one-person company: a Manager agent
decomposes a high-level goal into tasks, delegates them to specialized AI
workers, an independent QA/Auditor agent reviews every deliverable, and a
controlled revision loop (with a hard cap) ensures quality before the human
owner approves the final result.

```
Human Owner -> Manager Agent -> Specialized Workers -> QA/Auditor
     ^                                                    |
     +----------- Final Deliverable <- Manager <- Approved +
```

## What's implemented (MVP scope)

- 5 agents: Manager, Research, Marketing/Strategy, Builder, QA/Auditor
- Manager dynamically decomposes any objective into a task graph with
  real dependencies (not a hardcoded pipeline)
- Independent QA review with a structured, Pydantic-validated verdict
  (status / score / issues / required changes)
- Controlled revision loop with MAX_REVISIONS, falling back to
  WAITING_FOR_HUMAN rather than looping forever
- Automatic retry (MAX_TASK_RETRIES) for technical/transient failures
  (network errors, unparseable LLM responses) -- distinct from the QA
  revision loop above, so a temporary hiccup gets retried automatically
  instead of the task being marked permanently FAILED on the first blip
- Enforced task state machine (invalid transitions raise, not silently ignored)
- Real-time activity feed over WebSocket -- every event in the UI
  corresponds to an actual backend event, nothing is simulated
- Human approval endpoints (approve / reject / retry) for tasks stuck
  waiting on a human
- Full React/TypeScript dashboard: overview, project workspace, task
  board, agent workforce, QA review panel, revision history, activity
  timeline, deliverables

**Deliberately out of scope for this MVP** (per the original spec's own
"don't add complexity without purpose" rule): dynamic agent creation,
vector memory, Ollama wiring beyond the config flag, Celery/Redis.

## Architecture

```
Frontend (React + TS)
   | REST + WebSocket
FastAPI (backend/app/api/*) -- thin HTTP layer
   |
Orchestration Service (backend/app/services/orchestration.py)
   -- the REAL "Manager": planning, dependency resolution,
      the QA loop, the revision cap, human-approval fallback.
      Plain Python. Does not depend on CrewAI internals.
   | (one call at a time)
Agent Runner (backend/app/crews/agent_runner.py)
   -- wraps exactly one CrewAI Agent + Task + Crew per call
   |
CrewAI Agent -> Tools -> LLM (OpenRouter or Ollama)
```

This mirrors the Phase-1 recommendation from earlier in the build:
CrewAI is a tool the orchestrator calls for one unit of work at a time,
not the framework that owns the whole workflow. That's what makes the
QA loop, revision cap, and human-approval logic simple, testable, plain
Python (see backend/tests/test_qa_revision_loop.py) instead of fighting
CrewAI's own control flow.

## Running it locally

### Backend

```bash
cd backend
cp .env.example .env        # then fill in OPENROUTER_API_KEY
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Defaults to a local SQLite file (ai_company.db) -- zero external services
required to try it. Set DATABASE_URL in .env to point at PostgreSQL
instead; nothing else needs to change.

Visit http://localhost:8000/docs for the interactive API explorer.

### Frontend

```bash
cd frontend
cp .env.example .env        # defaults to http://localhost:8000, adjust if needed
npm install
npm run dev
```

Visit http://localhost:5173.

### Docker (all three services)

```bash
cp backend/.env.example backend/.env   # fill in OPENROUTER_API_KEY
docker compose up --build
```

## Running the tests

```bash
cd backend
pip install -r requirements.txt
pytest -v
```

14 tests, including the critical integration test (test_qa_revision_loop.py)
that runs a full reject -> revise -> approve cycle, and a max-revisions
test that confirms the system falls back to WAITING_FOR_HUMAN instead
of looping forever. Every LLM call in the tests is mocked -- they verify
OUR workflow logic, not the model's writing, so they run with no API
key and no network access.

## Environment variables

See backend/.env.example and frontend/.env.example for the full list.
The important ones:

```env
# backend/.env
LLM_PROVIDER=openrouter        # or "ollama"
OPENROUTER_API_KEY=your_key
MODEL_NAME=openai/gpt-4o-mini
DATABASE_URL=sqlite:///./ai_company.db
MAX_REVISIONS=2
MAX_TASK_RETRIES=2
```

## API reference

| Method | Path | Purpose |
|---|---|---|
| GET | /health | Liveness check |
| POST | /projects | Create a project |
| GET | /projects | List projects |
| GET | /projects/{id} | Get one project |
| POST | /projects/{id}/run | Start the Manager planning + execution (background) |
| POST | /projects/{id}/stop | Cancel a running project |
| GET | /projects/{id}/tasks | List a project's tasks |
| GET | /projects/{id}/events | Full event history |
| WS | /ws/projects/{id} | Live event stream |
| GET | /tasks/{id} | Task detail |
| GET | /tasks/{id}/output | Latest output |
| GET | /tasks/{id}/review | Latest QA review |
| GET | /tasks/{id}/history | All agent runs + reviews (version history) |
| POST | /tasks/{id}/approve | Human approves a WAITING_FOR_HUMAN task |
| POST | /tasks/{id}/reject | Human cancels a task |
| POST | /tasks/{id}/retry | Reset revision count and resume |
| GET | /agents | List the 5 agents + capabilities |
| GET | /agents/{name}/stats | Run/approval/revision counts |

## Try it

```bash
curl -X POST http://localhost:8000/projects \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Restaurant SaaS Launch",
    "goal": "Develop a launch strategy for an AI-powered restaurant management product targeting small restaurants in Pakistan."
  }'

curl -X POST http://localhost:8000/projects/1/run
```

Then open the frontend and watch the Manager plan tasks, delegate to
Research/Marketing/Builder, and QA review (and occasionally reject and
revise) each deliverable in real time.

## Project layout

```
backend/
  app/
    core/         settings, enums, the enforced task state machine
    database/     SQLAlchemy engine/session
    models/       Project, Task, AgentRun, Review, Event
    schemas/      Pydantic request/response + QA structured output
    agents/       the 5 CrewAI agent definitions + registry
    crews/        single-task CrewAI runner + prompt builders
    tools/        web search, file export
    services/     orchestration (the real engine), QA parsing,
                   event/WebSocket broadcast, project memory/context
    api/          FastAPI routers
  tests/          pytest -- state machine, QA parsing, CRUD, the
                   full reject->revise->approve integration test
frontend/
  src/
    components/   layout, dashboard, projects, tasks, agents,
                   reviews, ui primitives
    pages/        Dashboard, Projects, ProjectDetails, Tasks,
                   TaskDetails, Workforce, AgentDetails, Activity,
                   Deliverables, Settings
    hooks/        TanStack Query hooks per resource + WebSocket hook
    services/     typed API client
    store/        Zustand (sidebar state only)
    types/        TypeScript types mirroring the backend schemas
docker-compose.yml
```

## Known limitations / good next steps

- The orchestration loop runs tasks sequentially, not concurrently --
  fine for the MVP demo, worth revisiting if a project has many
  independent branches.
- run_project runs as a FastAPI BackgroundTasks call with its own
  DB session; for heavier load this is the natural place to swap in a
  proper task queue later, without changing the orchestration logic itself.
- The web_search tool scrapes DuckDuckGo's HTML endpoint to avoid
  requiring a paid search API key out of the box -- swap in a real
  search API in backend/app/tools/web_search.py for production use.
- No auth -- this is a single-owner local tool, per the "one-person
  company" premise. Add auth before exposing it beyond localhost.
