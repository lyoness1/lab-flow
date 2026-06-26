# LabFlow

LabFlow is a lab-result workflow service: accept inbound messages, process them through a durable pipeline, and expose status over HTTP.

- Architecture: [docs/labflow-design-document.md](docs/labflow-design-document.md)
- Contracts: [schemas/](schemas/) (JSON Schema) and [src/labflow/models/](src/labflow/models/) (Pydantic)
- Fixtures: [examples/](examples/)
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
  -d @examples/inputs/lab-message-normal-v0.json
```

Expected response (`202`):

```json
{
  "workflow_run_id": "wr_f81d4fae7dec",
  "message_id": "MSG-0001",
  "state": "RECEIVED"
}
```

Invalid payloads return `400` with a stable error envelope (see [design doc — Error responses](docs/labflow-design-document.md#error-responses)):

```json
{
  "status": 400,
  "code": "validation_error",
  "message": "Request validation failed",
  "details": [
    {"field": "observations.0.code", "message": "..."}
  ]
}
```
