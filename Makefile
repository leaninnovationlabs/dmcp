.PHONY: help install migrate start stop docker-build docker-run docker-stop docker-clean  appbundle clean

# Default port if not specified
PORT ?= 8000
APP_NAME ?= dmcp
APP_VERSION := $(shell grep "version:" bundles/$(APP_NAME)/appbundle.yml | head -n 1 | awk '{print $$2}')

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

db-migrate:
	uv run alembic upgrade head

db-truncate:
	uv run alembic downgrade base

start: db-migrate
	uv run main.py

stop:
	pkill -f "main.py"

docker-build:
	docker build -t $(APP_NAME):$(APP_VERSION) .

docker-run:
	docker run \
		--name dmcp \
		--env-file .env \
		-p 8000:8000 \
		-v $(PWD)/data:/app/data \
		datamcp:latest

docker-build-run: docker-build docker-run

docker-stop:
	docker stop dmcp || true
	docker rm dmcp || true

docker-clean: docker-stop
	docker rmi dmcp:latest || true

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

clean:
	rm -f $(APP_NAME) $(APP_NAME)-$(APP_VERSION).tar.gz
	rm -rf dist