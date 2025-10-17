.PHONY: help install migrate up down docker-build docker-up docker-down

# Default port if not specified
PORT ?= 8000
APP_NAME ?= dmcp
APP_VERSION := $(shell grep "version:" bundles/$(APP_NAME)/appbundle.yml | head -n 1 | awk '{print $$2}')

help:
	@echo "Available targets:"
	@echo "  help         - Show this help message"
	@echo "  install      - Install dependencies with uv"
	@echo "  lint         - Check code for issues"
	@echo "  lint-fix     - Auto-fix linting issues"
	@echo "  format       - Format code"
	@echo "  format-check - Check code formatting"
	@echo "  typecheck    - Run type checking"
	@echo "  check        - Run all checks (lint, format-check, typecheck)"
	@echo "  fix          - Auto-fix and format code"
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

lint:
	uv run ruff check .

lint-fix:
	uv run ruff check --fix .

format:
	uv run ruff format .

format-check:
	uv run ruff format --check .

typecheck:
	uv run mypy .

check: lint format-check typecheck

fix: lint-fix format

db-migrate:
	uv run alembic upgrade head

db-truncate:
	uv run alembic downgrade base

up: db-migrate
	uv run main.py

down:
	pkill -f "main.py"

docker-build:
	docker build -t $(APP_NAME):$(APP_VERSION) .

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


appbundle:
	@echo "Removing old $(APP_NAME).tar.gz and dist/ folder..."
	@rm -f $(APP_NAME)-$(APP_VERSION).tar.gz
	@rm -rf dist
	@echo "Creating temporary folder dist/$(APP_NAME)..."
	@mkdir -p dist/$(APP_NAME)
	@echo "Copying roles/ and actions/..."
	@cp -r bundles/${APP_NAME}/roles dist/$(APP_NAME)/
	@cp -r bundles/${APP_NAME}/actions dist/$(APP_NAME)/
	@cp bundles/${APP_NAME}/appbundle.yml dist/$(APP_NAME)/
	@cp bundles/${APP_NAME}/ansible.cfg dist/$(APP_NAME)/ansible.cfg
	@echo "Building Docker image via existing docker target..."
	@$(MAKE) docker-build
	@echo "Saving Docker image tar..."
	@docker save $(APP_NAME):$(APP_VERSION) | gzip > dist/docker-image.tar.gz
	@mkdir -p dist/$(APP_NAME)/images
	@mv dist/docker-image.tar.gz dist/$(APP_NAME)/images/$(APP_NAME).tar.gz
	@echo "Creating final tarball $(APP_NAME)-$(APP_VERSION).tar.gz..."
	@cd dist/${APP_NAME} && find . -type f -name '*.tgz' -o -name '*.tar.gz' -o -name '*.yml' -o -name 'ansible.cfg' | tar czf ../$(APP_NAME)-$(APP_VERSION).tar.gz -T -
	@echo "Appbundle created at dist/$(APP_NAME)-$(APP_VERSION).tar.gz"
