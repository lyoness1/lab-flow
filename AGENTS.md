# LabFlow agent instructions

LabFlow is built in small, reviewable increments. Do not commit unless the user asks.

## Source of truth

- `docs/labflow-design-document.md` — architecture and behavior
- `src/labflow/models/` — Pydantic models for **implemented** endpoints (API contracts; OpenAPI at `/docs`)
- `schemas/` — JSON Schema for **not-yet-implemented** endpoints only
- `tests/factories/` — test data built from Pydantic models
- `docs/contributing.md` — diagram regeneration and change workflow

Personal checklists and notes (`docs/backlog.md`, `docs/implementation-plan.md`, `docs/author-notes.md`) are gitignored and live only on the author's machine.

When the author asks **what's next**, **what's deferred**, or **what's in the backlog**, read `docs/backlog.md` first, then `docs/implementation-plan.md` for milestone order. Update those files when deferring work out of a PR.

## Contract changes

**Implemented endpoint** — update together:

1. design doc
2. Pydantic model(s) in `src/labflow/models/`
3. factories in `tests/factories/` when tests need sample payloads

When an endpoint ships, remove its JSON Schema file from `schemas/` if one exists.

**Not-yet-implemented endpoint** — JSON Schema in `schemas/` plus design doc as needed.

Contract validation is tested through endpoint behavior tests.

## Implementation rules

- Implement only what the user requested for the current milestone.
- Do not add Postgres tables, worker logic, queues, or Docker Compose before the design doc describes them for that milestone.
- Write or update tests for every behavior change.
- Keep models minimal — no fields the current milestone does not use.
- Run tests before reporting done.
- When editing markdown the user may have open in preview, warn them to reload from disk after agent writes.

## Repo layout (current)

- `docs/`, `schemas/`, `diagrams/` — design
- `src/labflow/app.py` — app factory and validation error handler
- `src/labflow/api/v0/` — versioned route modules (one file per resource)
- `src/labflow/models/` — Pydantic request/response models
- `src/labflow/utils.py` — small shared helpers (`create_id`, etc.)
- `tests/factories/` — test data factories
- `tests/` — pytest suite (httpx TestClient)

## Running locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pytest
uvicorn labflow.app:app --reload
```

Use `python -m uvicorn labflow.app:app --reload` if `uvicorn` is not on your PATH outside the venv.
