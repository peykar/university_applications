#!/usr/bin/env bash
set -euo pipefail

uv sync
uv run python manage.py makemigrations
uv run python manage.py migrate
uv run python manage.py populate_countries
uv run python manage.py check
