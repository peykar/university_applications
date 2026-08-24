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

See `docs/linting-and-quality.md` for Ruff, mypy, pytest, coverage and
pre-commit commands.

## Download RasaStudy data

```bash
make rasa-download
```

This downloads universities, programs, FAQ categories, FAQs, and referenced
public assets into `data/rasa/`.

See `docs/rasa-data.md`.

## Import downloaded RasaStudy data

```bash
make rasa-download
uv run python manage.py populate_countries
make rasa-import
```

See `docs/rasa-import.md`.

Detailed RasaStudy mapping is documented in `docs/rasa-mapping.md`.

Internal admin behavior is documented in `docs/admin.md`.

## Automated audit user

Copy `.env.example` to `.env` and configure the non-human system identity used
by management commands. Defaults are non-staff/non-superuser.

```bash
uv run python manage.py ensure_system_user
```

See `docs/configuration.md` and `docs/auditing.md`.

## Full-stack development

Backend:

```bash
uv sync --all-groups
uv run python manage.py migrate
uv run python manage.py runserver
```


Production-style backend:

```bash
make run-prod
```

Docker development:

```bash
make docker-up
```

See:
- `docs/deployment.md`
- `docs/i18n.md`
- `docs/public-and-api.md`
- `docs/public-frontend.md`

## Canonical public URL

Configure the public domain through `.env`:

```dotenv
SITE_URL=https://turkdemy.com
```

TurkDemy uses this to generate absolute links for emails, notifications and
other out-of-request contexts.

See `docs/site-url-and-email.md`.


## Web frontend

Django templates are the primary public frontend. There is no separate
React/Vite web application.

DRF remains available for integrations and future API clients.

See `docs/public-frontend.md`.
