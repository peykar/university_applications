sync:
	uv sync

migrate:
	uv run python manage.py migrate

makemigrations:
	uv run python manage.py makemigrations

run:
	uv run python manage.py runserver

test:
	uv run python manage.py test

check:
	uv run python manage.py check

countries:
	uv run python manage.py populate_countries
