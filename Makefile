.PHONY: help install migrate up down docker-build docker-up docker-down

# Default port if not specified
PORT ?= 8000

help:
	@echo "Available targets:"
	@echo "  help         - Show this help message"
	@echo "  install      - Install dependencies with uv"
	@echo "  migrate      - Run database migrations"
	@echo "  up        - Start the application (runs migrate first)"
	@echo "  down         - Stop the running application"
	@echo "  docker-build - Build Docker image"
	@echo "  docker-up   - Build and run Docker container"
	@echo "  docker-down  - Stop and remove Docker container"
	@echo ""
	@echo "Environment variables:"
	@echo "  PORT         - Port to use (default: 8000)"

install:
	uv sync

db-migrate:
	uv run alembic upgrade head

db-truncate:
	uv run alembic downgrade base

up: db-migrate
	uv run main.py

down:
	pkill -f "main.py"

docker-build:
	docker build -t datamcp:latest .

docker-up:
	docker run \
		--name dmcp \
		--env-file .env \
		-p 9000:8000 \
		-v $(PWD)/data:/app/data \
		datamcp:latest

docker-down:
	docker stop dmcp || true
	docker rm dmcp || true

