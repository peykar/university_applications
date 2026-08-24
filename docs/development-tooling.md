# Development tooling


## Pre-commit mypy

The mypy hook uses the project's uv-managed environment:

```bash
uv run mypy apps turkdemy
```

It deliberately uses `language: system` with `pass_filenames: false`.
`django-stubs` initializes Django while type checking, so mypy needs the same
runtime dependencies as the application itself. Using the uv environment
avoids duplicating the entire runtime dependency set in pre-commit's isolated
hook environment.

After dependency changes, run:

```bash
uv sync --all-groups
pre-commit clean
pre-commit install
```
