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
