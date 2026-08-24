# Development

## Requirements

- Python 3.11+
- uv

## Install dependencies

```bash
uv sync
```

## Bootstrap

```bash
./scripts/bootstrap.sh
```

The bootstrap script performs the core Django setup commands.

## Manual setup

```bash
uv sync
uv run python manage.py makemigrations university_applications
uv run python manage.py migrate
uv run python manage.py check
```

## Create admin user

```bash
uv run python manage.py createsuperuser
```

## Run development server

```bash
uv run python manage.py runserver
```

Then open:

```text
http://127.0.0.1:8000/
http://127.0.0.1:8000/admin/
```

## Tests

```bash
uv run python manage.py test university_applications
```

## Documentation rule

Whenever a code change affects architecture, models, relationships,
validation, authentication, setup, or business behavior, update the
corresponding file under `docs/` in the same change.

## Populate country reference data

```bash
uv run python manage.py populate_countries
```

This imports ISO country codes from `pycountry` and translated country names from Babel/CLDR.
