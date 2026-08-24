# Deployment

## Database

TurkDemy supports `DATABASE_URL` through `dj-database-url`.

Local development may omit it and use SQLite.

Production should use PostgreSQL:

```dotenv
DATABASE_URL=postgresql://user:password@db:5432/turkdemy
```

## Gunicorn

Production application server:

```bash
uv run gunicorn turkdemy.wsgi:application \
  --bind 0.0.0.0:8000 \
  --workers 3
```

## Docker

Development:

```bash
docker compose up --build
```

Production:

```bash
docker compose -f docker-compose.prod.yml up --build -d
```

Production Compose includes PostgreSQL, Django/Gunicorn, and the React/nginx
frontend.

## Readiness

`/health/` checks process liveness.

`/health/ready/` performs a database query (`SELECT 1`). It returns HTTP 503
when the database cannot be reached.
