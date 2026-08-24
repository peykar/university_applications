sync:
	uv sync --all-groups

migrate:
	uv run python manage.py migrate

makemigrations:
	uv run python manage.py makemigrations

run:
	uv run python manage.py runserver

countries:
	uv run python manage.py populate_countries

ruff:
	uv run ruff check .

format:
	uv run ruff check . --fix
	uv run ruff format .
	uv run black .

format-check:
	uv run ruff format --check .
	uv run black --check .

typecheck:
	uv run mypy apps turkdemy

test:
	uv run pytest

coverage:
	uv run pytest --cov=apps --cov=turkdemy --cov-report=term-missing

check:
	uv run ruff check .
	uv run ruff format --check .
	uv run black --check .
	uv run mypy apps turkdemy
	uv run python manage.py check
	uv run pytest

pre-commit-install:
	uv run pre-commit install

pre-commit:
	uv run pre-commit run --all-files

rasa-download:
	uv run python scripts/download_rasastudy.py --output data/rasa


rasa-import:
	uv run python manage.py import_rasa_data data/rasa

rasa-import-catalogue:
	uv run python manage.py import_rasa_catalogue data/rasa

rasa-import-content:
	uv run python manage.py import_rasa_content data/rasa

system-user:
	uv run python manage.py ensure_system_user


run-prod:
	uv run gunicorn turkdemy.wsgi:application --bind 0.0.0.0:8000 --workers 3

frontend-install:
	cd frontend && npm install

frontend-dev:
	cd frontend && npm run dev

frontend-build:
	cd frontend && npm run build

docker-up:
	docker compose up --build

docker-prod:
	docker compose -f docker-compose.prod.yml up --build -d

.PHONY: bootstrap setup migrate system-user countries

# Prepare a fresh local TurkDemy checkout.
# This intentionally does not download/import Rasa data.
bootstrap: setup migrate system-user countries

setup:
	uv sync --all-groups

migrate:
	uv run python manage.py migrate

system-user:
	uv run python manage.py ensure_system_user

countries:
	uv run python manage.py populate_countries
