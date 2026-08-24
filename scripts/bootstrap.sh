#!/usr/bin/env bash
set -euo pipefail

uv sync
uv run python manage.py makemigrations university_applications
uv run python manage.py migrate
uv run python manage.py check

echo
echo "Bootstrap complete."
echo "Create an admin user with: uv run python manage.py createsuperuser"
echo "Start the server with:     uv run python manage.py runserver"
