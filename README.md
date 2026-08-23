# University Applications

A complete runnable Django project for managing universities, programs, offerings, agents, students, documents, and university applications.

## Requirements

- Python 3.11+
- `uv`

## Fastest way to run

```bash
unzip university_applications_complete.zip
cd university_applications_complete

./scripts/bootstrap.sh
uv run python manage.py createsuperuser
uv run python manage.py runserver
```

Open:

- Home/status: http://127.0.0.1:8000/
- Django admin: http://127.0.0.1:8000/admin/

The default database is SQLite (`db.sqlite3`), so no PostgreSQL or other external database is required for local development.

## Manual setup

If you prefer to run every command yourself:

```bash
uv sync
uv run python manage.py makemigrations university_applications
uv run python manage.py migrate
uv run python manage.py check
uv run python manage.py createsuperuser
uv run python manage.py runserver
```

The first successful `uv sync` also creates `uv.lock`; commit that file to Git for reproducible installs.

## Tests

```bash
uv run python manage.py test university_applications
# or
uv run pytest
```

## Phone numbers

`User.cell` and `Student.cell` are validated using `phonenumbers` and normalized to E.164 format:

```text
+31 6 1234 5678 -> +31612345678
```

`User.cell_verified_at` is separate because number-format validation does not prove ownership.

## Project structure

```text
.
├── manage.py
├── pyproject.toml
├── .env.example
├── scripts/
│   └── bootstrap.sh
├── config/
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
└── university_applications/
    ├── models.py
    ├── admin.py
    ├── managers.py
    ├── services.py
    ├── validators.py
    ├── migrations/
    └── tests/
```

## Main model flow

```text
Country -> Province -> City -> University -> Program -> ProgramOffering
                                                     -> Application
Student -> StudentDocument ---------------------------> ApplicationDocument
Agent -> Student / Application
```

`Program` stores the academic identity of a program. `ProgramOffering` stores intake-specific academic year, semester, tuition, quota, and deadline data. `Application` points to a `ProgramOffering` and snapshots its applicable tuition/deposit values.
