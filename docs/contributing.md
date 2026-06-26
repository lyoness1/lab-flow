# Contributing to LabFlow

## Before you change behavior

1. Read [labflow-design-document.md](labflow-design-document.md).
2. If you change a contract, update together in one change set:
  - design doc
  - `schemas/` (JSON Schema)
  - `examples/`
  - Pydantic models in `src/labflow/models/`
3. Run tests before opening a PR.

## Contracts vs Python models

| Location | Purpose |
|---|---|
| `schemas/` | JSON Schema files — portable contract definitions |
| `src/labflow/models/` | Pydantic models — runtime validation and OpenAPI types |

Keep names aligned (for example `LabMessageCreateResponse` ↔ `lab-message-create-response-v0.schema.json`).

## API errors

Client-facing error responses use a stable JSON envelope documented in the design doc and defined in `schemas/error-response-v0.schema.json`. Implementations should return this shape for validation failures (`400`) and other client errors (`404`, `409`) unless an endpoint specifies otherwise.

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
