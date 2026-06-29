# LabFlow

LabFlow is a lab-result workflow service: accept inbound messages, process them through a durable pipeline, and expose status over HTTP.

- Architecture: [docs/labflow-design-document.md](docs/labflow-design-document.md)
- Implemented API schemas: [src/labflow/api/v0/](src/labflow/api/v0/) (OpenAPI at `/docs`)
- Database tables: [src/labflow/database/](src/labflow/database/)
- Future contracts: [schemas/](schemas/) and [examples/](examples/)
- Contributing (including diagrams): [docs/contributing.md](docs/contributing.md)

## Local setup

First-time setup on a new machine:

1. [Python](#python) — venv and install LabFlow
2. [PostgreSQL (Homebrew)](#postgresql-setup-homebrew) — install Postgres 16, create databases, env vars (matches CI)
3. [Run checks](#run-checks) — ruff and pytest
4. [Run the API](#run-the-api) — start the server and try endpoints

### Python

Requires Python 3.11+.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

### PostgreSQL setup (Homebrew)

Requires **PostgreSQL 16** (same major version as CI). LabFlow uses Homebrew locally so dev matches CI (`postgres:16` in GitHub Actions).

**Do not run Postgres.app at the same time** — both default to port `5432`. Quit Postgres.app and leave it stopped (or disable “Launch at login” in the app) before using Brew Postgres.

#### 1. Install and start

```bash
brew install postgresql@16
brew services start postgresql@16
```

Put Brew’s `psql` on your PATH (add to `~/.zshrc` so new shells pick it up):

```bash
export PATH="$(brew --prefix postgresql@16)/bin:$PATH"
```

Verify you are on **16**, not an older Postgres.app binary:

```bash
which psql          # should be .../postgresql@16/bin/psql
psql --version      # PostgreSQL 16.x (Homebrew)
pg_isready          # localhost:5432 - accepting connections
```

If `which psql` still points at Postgres.app, fix PATH order or open a new terminal after editing `~/.zshrc`.

#### 2. Create role and databases

The API and tests use **separate databases** so test runs do not touch dev data:

| Purpose | Database | Env var |
|---|---|---|
| Local API | `labflow` | `DATABASE_URL` |
| Tests | `labflow_test` | `TEST_DATABASE_URL` |

Run once (as your macOS user — Brew Postgres trusts local connections by default):

```bash
psql -d postgres <<'SQL'
CREATE USER labflow WITH PASSWORD 'labflow';
CREATE DATABASE labflow OWNER labflow;
CREATE DATABASE labflow_test OWNER labflow;
SQL
```

Re-running will error with “already exists”; that is fine.

#### 3. Environment variables

Defaults if unset:

```bash
export DATABASE_URL=postgresql+psycopg://labflow:labflow@localhost:5432/labflow
export TEST_DATABASE_URL=postgresql+psycopg://labflow:labflow@localhost:5432/labflow_test
```

#### Troubleshooting

| Problem | Fix |
|---|---|
| `Connection refused` on 5432 | `brew services start postgresql@16` |
| `role "labflow" does not exist` | Run the `psql` block in step 2 |
| Wrong Postgres version | Check `which psql`; PATH must prefer `postgresql@16` |
| Port already in use | Stop Postgres.app or other Postgres: `lsof -i :5432` |
| Stop Brew Postgres | `brew services stop postgresql@16` |

### Run checks

**CI runs:** ruff + pytest (Postgres 16 service, database `labflow_test`).

**Locally:**

```bash
ruff format --check .
ruff check .
pytest   # uses TEST_DATABASE_URL → labflow_test
```

Optional pre-push hook (ruff only — pytest runs in CI):

```bash
pre-commit install --hook-type pre-push
```

### Run the API

Activate the venv first (`source .venv/bin/activate`), then:

```bash
export DATABASE_URL=postgresql+psycopg://labflow:labflow@localhost:5432/labflow
uvicorn labflow.app:app --reload
```

If `uvicorn` is not found, use:

```bash
python -m uvicorn labflow.app:app --reload
```

### Try endpoints

Health check:

```bash
curl http://127.0.0.1:8000/api/v0/health
```

Expected response:

```json
{"status": "ok"}
```

Submit a lab message:

```bash
curl -X POST http://127.0.0.1:8000/api/v0/lab-messages \
  -H 'Content-Type: application/json' \
  -d "$(PYTHONPATH=tests python -c 'from factories.lab_message import lab_message_normal; import json; print(json.dumps(lab_message_normal().model_dump()))')"
```

Expected response (`202`):

```json
{
  "workflow_run_id": "wr_f81d4fae7dec",
  "message_id": "MSG-0001",
  "state": "RECEIVED"
}
```

Invalid payloads return `400` with a consistent error envelope (see [design doc — Error responses](docs/labflow-design-document.md#error-responses)).
