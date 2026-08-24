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
