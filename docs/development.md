# Development

## Setup

```bash
uv sync
uv run python manage.py makemigrations
uv run python manage.py migrate
uv run python manage.py populate_countries
uv run python manage.py createsuperuser
uv run python manage.py runserver
```

## Useful commands

```bash
make sync
make makemigrations
make migrate
make countries
make check
make test
make run
```

## Health endpoints

```text
/health/
/health/ready/
```

## System audit user

After migrations, the non-human audit identity can be created/validated with:

```bash
uv run python manage.py ensure_system_user
```

It is also created lazily by audited management commands. See `docs/auditing.md`.
