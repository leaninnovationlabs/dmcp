.PHONY: help install migrate start stop docker-build docker-run docker-stop docker-clean

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

install:
	uv sync

migrate:
	uv run alembic upgrade head

start: migrate
	uv run main.py

stop:
	pkill -f "main.py"

docker-build:
	docker build -t dbmcp:latest .

docker-run: docker-build
	docker run -d \
		--name dbmcp \
		-p 8000:8000 \
		-v $(PWD)/dbmcp.db:/app/dbmcp.db \
		dbmcp:latest

docker-stop:
	docker stop dbmcp || true
	docker rm dbmcp || true

docker-clean: docker-stop
	docker rmi dbmcp:latest || true