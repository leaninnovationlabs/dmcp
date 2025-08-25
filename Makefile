.PHONY: help install migrate start stop docker-build docker-run docker-stop docker-clean

# Default port if not specified
PORT ?= 8000

help:
	@echo "Available targets:"
	@echo "  help         - Show this help message"
	@echo "  install      - Install dependencies with uv"
	@echo "  migrate      - Run database migrations"
	@echo "  start        - Start the application (runs migrate first)"
	@echo "  stop         - Stop the running application"
	@echo "  docker-build - Build Docker image"
	@echo "  docker-run   - Build and run Docker container"
	@echo "  docker-stop  - Stop and remove Docker container"
	@echo "  docker-clean - Stop container and remove image"
	@echo ""
	@echo "Environment variables:"
	@echo "  PORT         - Port to use (default: 8000)"

install:
	uv sync

migrate:
	uv run alembic upgrade head

start: migrate
	uv run main.py

stop:
	pkill -f "main.py"

docker-build:
	docker build -t dmcp:latest .

docker-run:
	docker run \
		--name dmcp \
		--env-file .env \
		-p 8000:8000 \
		-v $(PWD)/dmcp.db:/app/dmcp.db \
		dmcp:latest

docker-build-run: docker-build docker-run

docker-stop:
	docker stop dmcp || true
	docker rm dmcp || true

docker-clean: docker-stop
	docker rmi dmcp:latest || true