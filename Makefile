.PHONY: install migrate start stop

install:
	uv sync

migrate:
	uv run alembic upgrade head

start: migrate
	uv run main.py

stop:
	pkill -f "main.py"