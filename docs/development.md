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


## Bootstrap a fresh checkout

After creating `.env`:

```bash
make bootstrap
```

This runs, in order:

1. `uv sync --all-groups`
2. `python manage.py migrate`
3. `python manage.py ensure_system_user`
4. `python manage.py populate_countries`

Rasa data is intentionally separate:

```bash
make rasa-download
make rasa-import
```

If the Rasa files are already present under `data/rasa`, only run:

```bash
make rasa-import
```
