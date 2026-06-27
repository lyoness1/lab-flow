# Contributing to LabFlow

## Before you change behavior

1. Read [labflow-design-document.md](labflow-design-document.md).
2. If you change a contract for an **implemented** endpoint, update together:
  - design doc
  - Pydantic models in `src/labflow/models/`
  - factories in `tests/factories/` when tests need sample data
3. Run checks before opening a PR (same commands as CI):

```bash
ruff format --check .
ruff check .
pytest
```

Or install the git hook once (runs ruff + pytest before every `git push`; CI still runs on PRs):

```bash
pip install -e ".[dev]"
pre-commit install --hook-type pre-push
```

Fix formatting and safe lint issues locally:

```bash
ruff format .
ruff check --fix .
```

## Contracts

| Status | Source of truth |
|---|---|
| Implemented endpoint | Pydantic models in `src/labflow/models/` (also in OpenAPI at `/docs`) |
| Not yet implemented | JSON Schema in `schemas/` |

When you implement an endpoint, add Pydantic models and test factories, then delete the JSON Schema file for that contract if present.

Test data for implemented endpoints lives in `tests/factories/` — not in `src/` and not as committed JSON under `examples/`.

## Design doc and diagrams

Diagrams live in `diagrams/` as Graphviz source (`.dot`) and rendered PNGs. GitHub renders PNGs linked from the design doc — **commit both** when you change a diagram.

### Regenerate PNGs after editing `.dot` files

Requires [Graphviz](https://graphviz.org/) (`dot` on your PATH):

```bash
for f in context state_machine data_model; do
  dot -Tpng "diagrams/$f.dot" -o "diagrams/$f.png"
done
```

On macOS with Homebrew, if `dot` is not found:

```bash
export PATH="/usr/local/opt/graphviz/bin:$PATH"
```

Verify PNGs changed before committing:

```bash
ls -la diagrams/*.png
```

## Personal notes

Personal files should be gitignored and stay on your machine.

## Pull requests

- One behavioral change per PR where possible.
- Expand `README.md` as the project gains runnable commands and setup steps.
