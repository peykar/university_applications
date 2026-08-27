.PHONY: \
	help setup bootstrap migrate makemigrations system-user countries run run-prod \
	test coverage check ruff format format-check typecheck pre-commit pre-commit-install \
	rasa-download rasa-import rasa-import-catalogue rasa-import-content rasa-sync \
	docker-up docker-prod

help:
	@echo "TurkDemy development commands"
	@echo ""
	@echo "  make bootstrap          Fresh backend setup (sync, migrate, system user, countries)"
	@echo "  make run                Run Django development server"
	@echo "  make rasa-download      Download RasaStudy data/assets"
	@echo "  make rasa-import        Import all downloaded RasaStudy data"
	@echo "  make rasa-sync          Download then import RasaStudy data"
	@echo "  make check              Run backend quality checks"
	@echo "  make docker-up          Run development Docker Compose"
	@echo "  make docker-prod        Run production Docker Compose"

setup:
	uv sync --all-groups

bootstrap: setup migrate system-user countries

makemigrations:
	uv run python manage.py makemigrations

migrate:
	uv run python manage.py migrate

system-user:
	uv run python manage.py ensure_system_user

countries:
	uv run python manage.py populate_countries

run:
	uv run python manage.py runserver

run-prod:
	uv run gunicorn turkdemy.wsgi:application --bind 0.0.0.0:8000 --workers 3

ruff:
	uv run ruff check .

format:
	uv run ruff check . --fix
	uv run ruff format .

format-check:
	uv run ruff format --check .

typecheck:
	uv run mypy apps turkdemy

test:
	uv run pytest

coverage:
	uv run pytest --cov=apps --cov=turkdemy --cov-report=term-missing

check:
	uv run ruff check .
	uv run ruff format --check .
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

rasa-sync: rasa-download rasa-import

docker-up:
	docker compose up --build

docker-prod:
	docker compose -f docker-compose.prod.yml up --build -d

phone-check:
	uv run python manage.py check_phone_library




# Spec-driven development helpers.
# Usage: make spec-new NAME=document-requirements
spec-new:
	@test -n "$(NAME)" || (echo "Usage: make spec-new NAME=<capability-name>" && exit 1)
	@test ! -e "docs/specs/$(NAME)" || (echo "docs/specs/$(NAME) already exists" && exit 1)
	cp -R docs/specs/_template "docs/specs/$(NAME)"
	@echo "Created docs/specs/$(NAME). Rename CAP-* requirement IDs before approval."

spec-status:
	@printf "TurkDemy specification files:\n"
	@find docs/specs -mindepth 2 -maxdepth 2 -name spec.md -not -path "*/_template/*" \
		-print | sort
