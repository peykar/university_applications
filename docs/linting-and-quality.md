# Linting and Code Quality

TurkDemy uses complementary development tools rather than relying on one linter.

## Tools

- **Ruff** — fast Python linting, import sorting, Django-specific checks, bugbear,
  pyupgrade, simplification and selected Ruff rules.
- **mypy + django-stubs** — static type checking with Django awareness.
- **pytest + pytest-django** — test runner.
- **coverage / pytest-cov** — test coverage reporting.
- **pre-commit** — runs quality checks before commits.

Ruff is the project's single formatter as well as its primary linter. The formatter
and lint configuration share a line length of `100`.

## Initial setup

```bash
uv sync --all-groups
uv run pre-commit install
```

## Common commands

Lint:

```bash
make ruff
```

Automatically fix safe lint issues and format:

```bash
make format
```

Check formatting without changing files:

```bash
make format-check
```

Type check:

```bash
make typecheck
```

Tests:

```bash
make test
```

Coverage:

```bash
make coverage
```

Run the complete local quality gate:

```bash
make check
```

Run every pre-commit hook manually:

```bash
make pre-commit
```

## Ruff rule groups

The project enables:

- `E` — pycodestyle errors
- `F` — Pyflakes
- `I` — import sorting
- `B` — flake8-bugbear
- `UP` — pyupgrade
- `SIM` — flake8-simplify
- `DJ` — flake8-django
- `RUF` — Ruff-specific rules

Migrations, generated static files, and uploaded media are excluded where
appropriate.

## Coverage

Coverage is branch-aware and currently has a minimum threshold of 70%.
Increase the threshold as the test suite matures.

## django-stubs / mypy compatibility

`django-stubs` includes a mypy plugin and must be kept within its supported mypy
range. TurkDemy currently targets Django 5.2 with `django-stubs` 5.2.x, so the
project installs the `compatible-mypy` extra and constrains mypy to `<1.20`.
This prevents plugin-construction failures caused by resolving mypy 1.20+ with
`django-stubs` 5.2.x.

After changing either dependency, refresh the lock file and run the full gate:

```bash
uv lock
uv sync --all-groups
make check
```
