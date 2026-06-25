# LabFlow agent instructions

LabFlow is built in small, reviewable increments. Do not commit unless the user asks.

## Source of truth

- `docs/labflow-design-document.md` — architecture and behavior
- `schemas/` — JSON Schema contracts (keep aligned with the design doc)
- `examples/` — fixture payloads for tests and docs
- `docs/contributing.md` — diagram regeneration and change workflow

Personal checklists and notes (`docs/implementation-plan.md`, `docs/author-notes.md`) are gitignored and live only on the author's machine.

## Contract changes

Update together in one change set:

1. design doc
2. `schemas/`
3. `examples/`

Schema validation tests against `examples/` ship with the lab message ingest PR (before `POST /lab-messages` merges).

## Implementation rules

- Implement only what the user requested for the current milestone.
- Do not add Postgres tables, worker logic, queues, or Docker Compose before the design doc describes them for that milestone.
- Write or update tests for every behavior change.
- Keep schemas minimal — no fields the current milestone does not use.
- Run tests before reporting done.
- When editing markdown the user may have open in preview, warn them to reload from disk after agent writes.

## Repo layout (current)

- `docs/`, `schemas/`, `examples/`, `diagrams/` — contracts and design
- `src/labflow/` — FastAPI application
- `tests/` — pytest suite (httpx TestClient)
