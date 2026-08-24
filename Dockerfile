FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

COPY pyproject.toml uv.lock* ./
RUN uv sync --no-dev || uv sync

COPY . .

RUN uv run python manage.py collectstatic --noinput || true

CMD ["uv", "run", "gunicorn", "turkdemy.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]
