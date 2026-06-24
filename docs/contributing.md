# Contributing to LabFlow

## Before you change behavior

1. Read [labflow-design-document.md](labflow-design-document.md).
2. If you change a contract, update together in one change set:
  - design doc
  - `schemas/`
  - `examples/`
3. Run tests before opening a PR. 

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
- Do not commit application code (Postgres, worker, broker) before the design doc describes it.
- Expand `README.md` as the project gains runnable commands and setup steps.

