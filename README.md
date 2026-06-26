# LabFlow

LabFlow is a lab-result workflow service: accept inbound messages, process them through a durable pipeline, and expose status over HTTP.

- Architecture: [docs/labflow-design-document.md](docs/labflow-design-document.md)
- Contracts: [src/labflow/models/](src/labflow/models/) (implemented endpoints; OpenAPI at `/docs`)
- Future contracts: [schemas/](schemas/) (JSON Schema for endpoints not yet built)
- Contributing (including diagrams): [docs/contributing.md](docs/contributing.md)

## Development

Requires Python 3.11+.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

### Run tests

```bash
pytest
```

Verbose:

```bash
pytest -v
```

### Run the API

Activate the venv first (`source .venv/bin/activate`), then:

```bash
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
