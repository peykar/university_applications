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

## Nginx request/upload size

TurkDemy accepts multipart uploads in several workflows, including agent logos,
agent documents, and applicant/message attachments. Nginx defaults
`client_max_body_size` to `1m`; requests larger than that are rejected by Nginx
with `413 Request Entity Too Large` before they ever reach Django.

The repository includes `deploy/nginx/turkdemy.conf.example`, which sets:

```nginx
client_max_body_size 25M;
```

For an existing production site, add the same directive to the active
`server { ... }` block for `turkdemy.com` (or to `http { ... }` if the limit
should apply to every site), then validate and reload Nginx:

```bash
sudo nginx -t
sudo systemctl reload nginx
```

To see which configuration Nginx is actually using:

```bash
sudo nginx -T | grep -n client_max_body_size
```

The limit is deliberately enforced at the reverse proxy. Do not set it to an
unbounded value. If the application later needs files larger than 25 MB, raise
this value intentionally and keep application-level file validation aligned
with it.
