# LabFlow agent instructions

LabFlow is built in small, reviewable increments. Do not commit unless the user asks.

## Commits

Use [Conventional Commits](https://www.conventionalcommits.org/) for every commit:

```
<type>(<optional scope>): <short description>
```

Common types: `feat`, `fix`, `docs`, `test`, `refactor`, `ci`, `chore`, `style`.

Examples:

- `feat(api): accept lab messages with validation envelope`
- `ci: add GitHub Actions for pytest and ruff`
- `docs: update contributing workflow for factories`

## Source of truth

- `docs/labflow-design-document.md` — architecture and behavior
- `src/labflow/database/` — SQLModel **table** classes (Postgres ORM)
- `src/labflow/api/v0/` — route handlers plus Pydantic request/response schemas per resource
- `schemas/` — JSON Schema for endpoints **not yet** implemented in Python (for example `WorkflowRunResponse`)
- `examples/` — JSON fixtures paired with those schemas (not for implemented endpoints)
- `tests/factories/` — test data built from implemented API schemas
- `docs/contributing.md` — diagram regeneration and change workflow

Personal checklists and notes (`docs/backlog.md`, `docs/implementation-plan.md`, `docs/author-notes.md`) are gitignored and live only on the author's machine.

When the author asks **what's next**, **what's deferred**, or **what's in the backlog**, read `docs/backlog.md` first, then `docs/implementation-plan.md` for milestone order. Update those files when deferring work out of a PR.

## Directory layout (models vs API schemas)

This project uses **option (a)** — the layout common in production FastAPI services at moderate scale:

| Layer | Location | Contents |
|---|---|---|
| **Database / ORM** | `src/labflow/database/` | SQLModel `table=True` classes, engine, sessions |
| **HTTP API** | `src/labflow/api/v0/` | Routes + Pydantic schemas (`LabMessagesBody`, `HealthResponse`, `ApiErrorResponse`, …) |

Pydantic-only types that belong to a specific route live in that route's module. Shared error envelopes live in `api/v0/errors.py`.

Alternatives we did **not** choose:

- **(b)** single `models/` for tables and schemas — blurs persistence vs HTTP boundaries as the project grows.
- **(c)** `models/` for all Pydantic + `database/` for tables — splits related API types across two trees; useful at very large scale with a dedicated `schemas/` package, but heavier than LabFlow v0 needs.

## Contract changes

**Implemented endpoint** — update together:

1. design doc
2. table SQLModel class(es) in `src/labflow/database/`
3. request/response Pydantic schemas in `src/labflow/api/v0/<resource>.py`
4. factories in `tests/factories/` when tests need sample payloads
5. remove JSON Schema and examples for that endpoint

Contract validation is tested through endpoint behavior tests.

## Implementation rules

- Implement only what the user requested for the current milestone.
- Do not add Postgres tables, worker logic, queues, or Docker Compose before the design doc describes them for that milestone.
- Write or update tests for every behavior change.
- Keep models minimal — no fields the current milestone does not use.
- Run tests before reporting done (requires PostgreSQL; see README).
- When editing markdown the user may have open in preview, warn them to reload from disk after agent writes.

## Repo layout (current)

- `docs/`, `diagrams/`, `schemas/`, `examples/` — design and not-yet-implemented contracts
- `src/labflow/app.py` — app factory and validation error handler
- `src/labflow/database/` — SQLModel tables, engine, sessions
- `src/labflow/api/v0/` — routes and Pydantic API schemas per resource
- `src/labflow/utils.py` — shared helpers (`create_id`, `compute_payload_hash`, etc.)
- `tests/factories/` — test data factories
- `tests/` — pytest suite (httpx TestClient, PostgreSQL)

## Running locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
export DATABASE_URL=postgresql+psycopg://labflow:labflow@localhost:5432/labflow
pre-commit install --hook-type pre-push   # ruff + pytest before push
pytest
uvicorn labflow.app:app --reload
```

Use `python -m uvicorn labflow.app:app --reload` if `uvicorn` is not on your PATH outside the venv.
