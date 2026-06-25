# LabFlow

LabFlow is a lab-result workflow service: accept inbound messages, process them through a durable pipeline, and expose status over HTTP.

- Architecture: [docs/labflow-design-document.md](docs/labflow-design-document.md)
- Contracts: [schemas/](schemas/)
- Fixtures: [examples/](examples/)
- Contributing (including diagrams): [docs/contributing.md](docs/contributing.md)

## Development

Requires Python 3.11+.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pytest
```

Run the API locally:

```bash
uvicorn labflow.app:app --reload
curl http://127.0.0.1:8000/api/v0/health
```

Expected response:

```json
{"status": "ok"}
```
