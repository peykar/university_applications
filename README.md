# TurkDemy

TurkDemy is a Django-based university discovery, agency management, student
dossier, and university application platform.

## Quick start

```bash
uv sync
uv run python manage.py makemigrations
uv run python manage.py migrate
uv run python manage.py populate_countries
uv run python manage.py createsuperuser
uv run python manage.py runserver
```

Open:

```text
http://127.0.0.1:8000/
http://127.0.0.1:8000/admin/
http://127.0.0.1:8000/health/
http://127.0.0.1:8000/health/ready/
```

Project documentation lives in `docs/`.

## Code quality

Install development dependencies and Git hooks:

```bash
uv sync --all-groups
uv run pre-commit install
```

Run the complete quality gate:

```bash
make check
```

See `docs/linting-and-quality.md` for Ruff, Black, mypy, pytest, coverage and
pre-commit commands.
