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
