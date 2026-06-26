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
2. `schemas/` (JSON Schema)
3. `examples/`
4. Pydantic models under `src/labflow/models/`

JSON Schema filenames and Pydantic class names should match (for example `lab-message-create-response-v0.schema.json` ↔ `LabMessageCreateResponse`).

Contract validation is tested through endpoint behavior tests — not standalone schema-only suites.

## Implementation rules

- Implement only what the user requested for the current milestone.
- Do not add Postgres tables, worker logic, queues, or Docker Compose before the design doc describes them for that milestone.
- Write or update tests for every behavior change.
- Keep schemas minimal — no fields the current milestone does not use.
- Run tests before reporting done.
- When editing markdown the user may have open in preview, warn them to reload from disk after agent writes.

## Repo layout (current)

- `docs/`, `schemas/`, `examples/`, `diagrams/` — contracts and design
- `src/labflow/app.py` — app factory and global exception handlers
- `src/labflow/api/v0/` — versioned route modules (one file per resource)
- `src/labflow/models/` — Pydantic request/response models (FastAPI convention)
- `src/labflow/utils.py` — small shared helpers (`create_id`, etc.)
- `tests/` — pytest suite (httpx TestClient)

Root `schemas/` holds JSON Schema contract files. `src/labflow/models/` holds the Python types that implement those contracts at runtime — different layers, different names.

## Running locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pytest
uvicorn labflow.app:app --reload
```

Use `python -m uvicorn labflow.app:app --reload` if `uvicorn` is not on your PATH outside the venv.
