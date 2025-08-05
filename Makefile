# Makefile for DBMCP Infrastructure and Deployment
# Usage: make <target> ENV=<environment>

# Default values
ENV ?= development
IMAGE_TAG ?= latest
FORCE_REDEPLOY ?= $(shell date +%s)

# Derived variables
APP_NAME := dbmcp
CONFIG_FILE := infra/config/$(ENV).yml
DOCKER_ENV_FILE := infra/config/$(ENV).env
TERRAFORM_DIR := infra/terraform

# Check if environment file exists
ifeq ($(wildcard $(CONFIG_FILE)),)
$(error Configuration file $(CONFIG_FILE) does not exist. Available: $(wildcard infra/config/*.yml))
endif

# Extract AWS region from config file (with fallback)
AWS_REGION ?= $(shell grep -E '^region:' $(CONFIG_FILE) 2>/dev/null | awk '{print $$2}' | tr -d '"' || echo "us-east-1")

# Load ECR repository URL from terraform output or fallback
ECR_REPOSITORY_URL := $(shell cd $(TERRAFORM_DIR) 2>/dev/null && terraform output -raw ecr_repository_url 2>/dev/null || echo "")

# Colors for output
RED := \033[0;31m
GREEN := \033[0;32m
YELLOW := \033[0;33m
BLUE := \033[0;34m
NC := \033[0m # No Color

.PHONY: help install build build-fresh push deploy destroy clean test lint format token docker-run docker-run-fresh docker-dev check-env check-aws check-tools ec2-check ec2-deploy ec2-start ec2-stop ec2-upgrade ec2-status ec2-ssh ec2-logs

# Default target
all: check-env check-aws check-tools build push deploy

## Help
help: ## Show this help message
	@echo "$(BLUE)DBMCP Infrastructure and Deployment$(NC)"
	@echo ""
	@echo "$(YELLOW)Usage:$(NC)"
	@echo "  make <target> ENV=<environment>"
	@echo ""
	@echo "$(YELLOW)Available environments:$(NC)"
	@for file in infra/config/*.yml; do \
		env=$$(basename $$file .yml); \
		echo "  - $$env"; \
	done
	@echo ""
	@echo "$(YELLOW)Targets:$(NC)"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  $(GREEN)%-15s$(NC) %s\n", $$1, $$2}' $(MAKEFILE_LIST)

## Environment Checks
check-env: ## Check if environment is valid
	@echo "$(BLUE)Checking environment: $(ENV)$(NC)"
	@if [ ! -f "$(CONFIG_FILE)" ]; then \
		echo "$(RED)Error: Configuration file $(CONFIG_FILE) not found$(NC)"; \
		exit 1; \
	fi
	@echo "$(GREEN)✓ Environment $(ENV) is valid$(NC)"

check-aws: ## Check AWS CLI configuration
	@echo "$(BLUE)Checking AWS configuration...$(NC)"
	@if ! aws sts get-caller-identity >/dev/null 2>&1; then \
		echo "$(RED)Error: AWS CLI not configured or credentials invalid$(NC)"; \
		echo "Please run 'aws configure' or set AWS environment variables"; \
		exit 1; \
	fi
	@echo "$(GREEN)✓ AWS credentials are valid$(NC)"
	@echo "Account: $$(aws sts get-caller-identity --query Account --output text)"
	@echo "Region: $(AWS_REGION)"

check-tools: ## Check required tools
	@echo "$(BLUE)Checking required tools...$(NC)"
	@command -v docker >/dev/null 2>&1 || { echo "$(RED)Error: docker is required but not installed$(NC)"; exit 1; }
	@command -v terraform >/dev/null 2>&1 || { echo "$(RED)Error: terraform is required but not installed$(NC)"; exit 1; }
	@echo "$(GREEN)✓ All required tools are available$(NC)"

## Development
install: ## Install development dependencies
	@echo "$(BLUE)Installing development dependencies...$(NC)"
	uv sync --dev
	@echo "$(GREEN)✓ Dependencies installed$(NC)"

test: ## Run tests
	@echo "$(BLUE)Running tests...$(NC)"
	uv run pytest tests/ -v
	@echo "$(GREEN)✓ Tests completed$(NC)"

lint: ## Run linters
	@echo "$(BLUE)Running linters...$(NC)"
	uv run black --check app/
	uv run isort --check-only app/
	uv run flake8 app/
	@echo "$(GREEN)✓ Linting completed$(NC)"

format: ## Format code
	@echo "$(BLUE)Formatting code...$(NC)"
	uv run black app/
	uv run isort app/
	@echo "$(GREEN)✓ Code formatted$(NC)"

token: ## Generate a new JWT bearer token for API authentication
	@echo "$(BLUE)Generating JWT bearer token...$(NC)"
	uv run scripts/apptoken.py
	@echo "$(GREEN)✓ Token generated$(NC)"

## Infrastructure
terraform-init: check-env ## Initialize Terraform
	@echo "$(BLUE)Initializing Terraform...$(NC)"
	cd $(TERRAFORM_DIR) && terraform init -backend-config=backend-$(ENV).hcl
	@echo "$(GREEN)✓ Terraform initialized$(NC)"

terraform-plan: terraform-init ## Plan Terraform changes
	@echo "$(BLUE)Planning infrastructure changes for $(ENV)...$(NC)"
	cd $(TERRAFORM_DIR) && terraform plan \
		-var="environment=$(ENV)" \
		-var="aws_region=$(AWS_REGION)" \
		-var="image_tag=$(IMAGE_TAG)" \
		-var="force_redeploy=$(FORCE_REDEPLOY)"

terraform-apply: terraform-init ## Apply Terraform changes
	@echo "$(BLUE)Applying infrastructure changes for $(ENV)...$(NC)"
	cd $(TERRAFORM_DIR) && terraform apply -auto-approve \
		-var="environment=$(ENV)" \
		-var="aws_region=$(AWS_REGION)" \
		-var="image_tag=$(IMAGE_TAG)" \
		-var="force_redeploy=$(FORCE_REDEPLOY)"
	@echo "$(GREEN)✓ Infrastructure deployed$(NC)"

terraform-destroy: terraform-init ## Destroy Terraform infrastructure
	@echo "$(YELLOW)⚠️  WARNING: This will destroy all infrastructure for $(ENV)$(NC)"
	@read -p "Are you sure? (yes/no): " confirm && [ "$$confirm" = "yes" ]
	cd $(TERRAFORM_DIR) && terraform destroy -auto-approve \
		-var="environment=$(ENV)" \
		-var="aws_region=$(AWS_REGION)"
	@echo "$(GREEN)✓ Infrastructure destroyed$(NC)"

terraform-output: ## Show Terraform outputs
	@cd $(TERRAFORM_DIR) && terraform output

## Docker Operations
build: check-env ## Build Docker images
	@echo "$(BLUE)Building Docker images for $(ENV)...$(NC)"
	docker build -f Dockerfile.fastapi -t $(APP_NAME)-fastapi:$(IMAGE_TAG) .
	docker build -f Dockerfile.mcp -t $(APP_NAME)-mcp:$(IMAGE_TAG) .
	@echo "$(GREEN)✓ Docker images built: $(APP_NAME)-fastapi:$(IMAGE_TAG), $(APP_NAME)-mcp:$(IMAGE_TAG)$(NC)"

build-fresh: check-env ## Build Docker images without cache (force fresh build)
	@echo "$(BLUE)Building fresh Docker images for $(ENV) (no cache)...$(NC)"
	docker build --no-cache -f Dockerfile.fastapi -t $(APP_NAME)-fastapi:$(IMAGE_TAG) .
	docker build --no-cache -f Dockerfile.mcp -t $(APP_NAME)-mcp:$(IMAGE_TAG) .
	@echo "$(GREEN)✓ Fresh Docker images built: $(APP_NAME)-fastapi:$(IMAGE_TAG), $(APP_NAME)-mcp:$(IMAGE_TAG)$(NC)"

docker-run: build ## Run Docker container locally
	@echo "$(BLUE)Starting Docker container locally...$(NC)"
	docker run --rm -p 8002:8000 \
		--env-file $(DOCKER_ENV_FILE) \
		$(APP_NAME):$(IMAGE_TAG)

docker-run-fresh: build-fresh ## Run Docker container with fresh build (no cache)
	@echo "$(BLUE)Starting Docker container with fresh build...$(NC)"
	docker run --rm -p 8002:8000 \
		--env-file $(DOCKER_ENV_FILE) \
		$(APP_NAME):$(IMAGE_TAG)

docker-dev: ## Run Docker container with volume mount for live frontend development
	@echo "$(BLUE)Starting Docker container in development mode with live reload...$(NC)"
	docker build -t $(APP_NAME):$(IMAGE_TAG) .
	docker run --rm -p 8002:8000 \
		--env-file $(DOCKER_ENV_FILE) \
		-v $(PWD)/frontend:/app/frontend \
		$(APP_NAME):$(IMAGE_TAG)

## ECR Operations
ecr-login: check-aws ## Login to ECR
	@echo "$(BLUE)Logging into ECR...$(NC)"
	aws ecr get-login-password --region $(AWS_REGION) | \
		docker login --username AWS --password-stdin $$(aws sts get-caller-identity --query Account --output text).dkr.ecr.$(AWS_REGION).amazonaws.com
	@echo "$(GREEN)✓ ECR login successful$(NC)"

ecr-create: terraform-init ## Create ECR repository
	@echo "$(BLUE)Creating ECR repository...$(NC)"
	cd $(TERRAFORM_DIR) && terraform apply -target=module.ecr -auto-approve \
		-var="environment=$(ENV)" \
		-var="aws_region=$(AWS_REGION)"
	@echo "$(GREEN)✓ ECR repository created$(NC)"

get-ecr-url: ## Get ECR repository URLs
	@FASTAPI_ECR_URL=$$(cd $(TERRAFORM_DIR) 2>/dev/null && terraform output -raw ecr_fastapi_repository_url 2>/dev/null || echo ""); \
	MCP_ECR_URL=$$(cd $(TERRAFORM_DIR) 2>/dev/null && terraform output -raw ecr_mcp_repository_url 2>/dev/null || echo ""); \
	if [ -z "$$FASTAPI_ECR_URL" ] || [ -z "$$MCP_ECR_URL" ]; then \
		echo "$(YELLOW)ECR repository URLs not found. Creating ECR repositories first...$(NC)"; \
		$(MAKE) ecr-create ENV=$(ENV); \
		FASTAPI_ECR_URL=$$(cd $(TERRAFORM_DIR) && terraform output -raw ecr_fastapi_repository_url); \
		MCP_ECR_URL=$$(cd $(TERRAFORM_DIR) && terraform output -raw ecr_mcp_repository_url); \
	fi; \
	echo "$(GREEN)ECR Repository URLs:$(NC)"; \
	echo "$(GREEN)  FastAPI: $$FASTAPI_ECR_URL$(NC)"; \
	echo "$(GREEN)  MCP: $$MCP_ECR_URL$(NC)"

tag-and-push: build ecr-login get-ecr-url ## Tag and push images to ECR
	@FASTAPI_ECR_URL=$$(cd $(TERRAFORM_DIR) 2>/dev/null && terraform output -raw ecr_fastapi_repository_url 2>/dev/null || echo ""); \
	MCP_ECR_URL=$$(cd $(TERRAFORM_DIR) 2>/dev/null && terraform output -raw ecr_mcp_repository_url 2>/dev/null || echo ""); \
	if [ -z "$$FASTAPI_ECR_URL" ] || [ -z "$$MCP_ECR_URL" ]; then \
		echo "$(RED)Error: ECR repository URLs not found. Run 'make ecr-create' first.$(NC)"; \
		exit 1; \
	fi; \
	echo "$(BLUE)Tagging and pushing images to ECR...$(NC)"; \
	docker tag $(APP_NAME)-fastapi:$(IMAGE_TAG) $$FASTAPI_ECR_URL:$(IMAGE_TAG); \
	docker tag $(APP_NAME)-mcp:$(IMAGE_TAG) $$MCP_ECR_URL:$(IMAGE_TAG); \
	docker push $$FASTAPI_ECR_URL:$(IMAGE_TAG); \
	docker push $$MCP_ECR_URL:$(IMAGE_TAG); \
	echo "$(GREEN)✓ Images pushed to ECR:$(NC)"; \
	echo "$(GREEN)  FastAPI: $$FASTAPI_ECR_URL:$(IMAGE_TAG)$(NC)"; \
	echo "$(GREEN)  MCP: $$MCP_ECR_URL:$(IMAGE_TAG)$(NC)"

push: tag-and-push ## Alias for tag-and-push

## Deployment
deploy: ec2-deploy ## Deploy application to EC2 (default)

redeploy: ec2-upgrade ## Force redeploy with upgrade


## Cleanup
clean-docker: ## Clean up Docker images and containers
	@echo "$(BLUE)Cleaning up Docker resources...$(NC)"
	docker system prune -f
	@echo "$(GREEN)✓ Docker cleanup completed$(NC)"

clean-terraform: ## Clean Terraform state and cache
	@echo "$(BLUE)Cleaning Terraform cache...$(NC)"
	rm -rf $(TERRAFORM_DIR)/.terraform
	rm -f $(TERRAFORM_DIR)/.terraform.lock.hcl
	rm -f $(TERRAFORM_DIR)/terraform.tfstate*
	@echo "$(GREEN)✓ Terraform cleanup completed$(NC)"

destroy: terraform-destroy ## Destroy all infrastructure

clean: clean-docker clean-terraform ## Clean all local artifacts

## CI/CD Targets
ci-build: check-tools build ## CI: Build image
ci-test: check-tools test lint ## CI: Run all tests and linting  
ci-deploy: check-env check-aws build push ec2-deploy ## CI: Full deployment pipeline

## RDS Test Database Operations
rds-test-up: check-env check-aws terraform-init ## Create RDS test instance and run migrations
	@echo "$(BLUE)Creating RDS test instance for $(ENV)...$(NC)"
	@# Apply only RDS module
	cd $(TERRAFORM_DIR) && terraform apply -target=module.rds_test -auto-approve \
		-var="environment=$(ENV)" \
		-var="aws_region=$(AWS_REGION)" \
		-var="image_tag=$(IMAGE_TAG)" \
		-var="force_redeploy=$(FORCE_REDEPLOY)"
	@echo "$(GREEN)✓ RDS test instance created$(NC)"
	@echo "$(BLUE)Running warehouse schema migrations...$(NC)"
	@$(MAKE) rds-test-migrate ENV=$(ENV)
	@echo "$(GREEN)✓ RDS test database ready for testing$(NC)"

rds-test-migrate: check-env ## Run warehouse migrations against RDS test instance
	@echo "$(BLUE)Running warehouse migrations for $(ENV)...$(NC)"
	@# Get database URL from Parameter Store and run migrations
	@WAREHOUSE_DATABASE_URL=$$(aws ssm get-parameter \
		--region $(AWS_REGION) \
		--name "/$(ENV)/dbmcp/test-db/url" \
		--with-decryption \
		--query 'Parameter.Value' \
		--output text 2>/dev/null || echo ""); \
	if [ -z "$$WAREHOUSE_DATABASE_URL" ]; then \
		echo "$(RED)Error: RDS test instance not found. Run 'make rds-test-up' first.$(NC)"; \
		exit 1; \
	fi; \
	export WAREHOUSE_DATABASE_URL="$$WAREHOUSE_DATABASE_URL"; \
	echo "$(BLUE)Running migrations against: $$(echo $$WAREHOUSE_DATABASE_URL | sed 's/:.*@/:***@/')$(NC)"; \
	uv run alembic -c alembic-warehouse.ini upgrade head
	@echo "$(GREEN)✓ Warehouse migrations completed$(NC)"

rds-test-down: check-env check-aws terraform-init ## Destroy RDS test instance
	@echo "$(YELLOW)⚠️  WARNING: This will destroy the RDS test instance for $(ENV)$(NC)"
	@read -p "Are you sure? (yes/no): " confirm && [ "$$confirm" = "yes" ]
	cd $(TERRAFORM_DIR) && terraform destroy -target=module.rds_test -auto-approve \
		-var="environment=$(ENV)" \
		-var="aws_region=$(AWS_REGION)"
	@echo "$(GREEN)✓ RDS test instance destroyed$(NC)"

rds-test-status: check-env check-aws ## Show RDS test instance status
	@echo "$(BLUE)RDS test instance status for $(ENV):$(NC)"
	@RDS_ENDPOINT=$$(cd $(TERRAFORM_DIR) 2>/dev/null && terraform output -raw rds_test_endpoint 2>/dev/null || echo ""); \
	if [ -z "$$RDS_ENDPOINT" ] || [ "$$RDS_ENDPOINT" = "null" ]; then \
		echo "$(YELLOW)RDS test instance not found or not deployed$(NC)"; \
	else \
		echo "$(GREEN)RDS Endpoint: $$RDS_ENDPOINT$(NC)"; \
		INSTANCE_ID=$$(cd $(TERRAFORM_DIR) && terraform output -raw rds_test_instance_id 2>/dev/null || echo ""); \
		if [ -n "$$INSTANCE_ID" ]; then \
			aws rds describe-db-instances --region $(AWS_REGION) --db-instance-identifier "$$INSTANCE_ID" \
				--query 'DBInstances[0].{Status:DBInstanceStatus,Engine:Engine,Class:DBInstanceClass,Storage:AllocatedStorage}' \
				--output table 2>/dev/null || echo "$(YELLOW)Instance details not available$(NC)"; \
		fi; \
	fi

rds-test-connect: check-env check-aws ## Show connection command for RDS test instance
	@echo "$(BLUE)RDS test instance connection info for $(ENV):$(NC)"
	@WAREHOUSE_DATABASE_URL=$$(aws ssm get-parameter \
		--region $(AWS_REGION) \
		--name "/$(ENV)/dbmcp/test-db/url" \
		--with-decryption \
		--query 'Parameter.Value' \
		--output text 2>/dev/null || echo ""); \
	if [ -z "$$WAREHOUSE_DATABASE_URL" ]; then \
		echo "$(RED)Error: RDS test instance not found. Run 'make rds-test-up' first.$(NC)"; \
		exit 1; \
	fi; \
	echo "$(GREEN)Database URL (use with psql or your preferred client):$(NC)"; \
	echo "$$WAREHOUSE_DATABASE_URL" | sed 's/postgresql+asyncpg/postgresql/'; \
	echo ""; \
	echo "$(BLUE)Example psql connection:$(NC)"; \
	echo "psql \"$$(echo $$WAREHOUSE_DATABASE_URL | sed 's/postgresql+asyncpg/postgresql/')\""

## EC2 Simple Deployment Operations
ec2-check: ## Check Ansible requirements
	@echo "$(BLUE)Checking Ansible requirements...$(NC)"
	@uv run ansible-playbook --version >/dev/null 2>&1 || { echo "$(RED)Error: ansible-playbook is required but not installed$(NC)"; exit 1; }
	@echo "$(GREEN)✓ Ansible requirements satisfied$(NC)"

ec2-deploy: check-env check-aws terraform-apply ec2-check tag-and-push ## Deploy to EC2 using Terraform + Ansible
	@echo "$(BLUE)Deploying DBMCP to EC2 for $(ENV)...$(NC)"
	@EC2_PUBLIC_IP=$$(cd $(TERRAFORM_DIR) && terraform output -raw ec2_public_ip); \
	echo "$(BLUE)Updating Ansible inventory with EC2 IP: $$EC2_PUBLIC_IP$(NC)"; \
	sed -i.bak "s/ansible_host:.*/ansible_host: $$EC2_PUBLIC_IP/" infra/ansible/inventory/$(ENV).yml; \
	echo "$(BLUE)Running Ansible deployment playbook...$(NC)"; \
	uv run ansible-playbook -i infra/ansible/inventory/$(ENV).yml infra/ansible/playbooks/deploy.yml
	@echo "$(GREEN)✓ DBMCP deployed to EC2$(NC)"

ec2-start: check-env ec2-check ## Start DBMCP services on EC2
	@echo "$(BLUE)Starting DBMCP services on EC2 for $(ENV)...$(NC)"
	@uv run ansible-playbook -i infra/ansible/inventory/$(ENV).yml infra/ansible/playbooks/start.yml
	@echo "$(GREEN)✓ DBMCP services started$(NC)"

ec2-stop: check-env ec2-check ## Stop DBMCP services on EC2
	@echo "$(BLUE)Stopping DBMCP services on EC2 for $(ENV)...$(NC)"
	@uv run ansible-playbook -i infra/ansible/inventory/$(ENV).yml infra/ansible/playbooks/stop.yml
	@echo "$(GREEN)✓ DBMCP services stopped$(NC)"

ec2-upgrade: check-env ec2-check tag-and-push ## Upgrade DBMCP services on EC2
	@echo "$(BLUE)Upgrading DBMCP services on EC2 for $(ENV)...$(NC)"
	@uv run ansible-playbook -i infra/ansible/inventory/$(ENV).yml infra/ansible/playbooks/upgrade.yml
	@echo "$(GREEN)✓ DBMCP services upgraded$(NC)"

ec2-status: check-env check-aws ## Show EC2 deployment status
	@echo "$(BLUE)EC2 deployment status for $(ENV):$(NC)"
	@EC2_INSTANCE_ID=$$(cd $(TERRAFORM_DIR) 2>/dev/null && terraform output -raw ec2_instance_id 2>/dev/null || echo ""); \
	if [ -z "$$EC2_INSTANCE_ID" ] || [ "$$EC2_INSTANCE_ID" = "null" ]; then \
		echo "$(YELLOW)EC2 instance not found or not deployed$(NC)"; \
	else \
		echo "$(GREEN)Instance ID: $$EC2_INSTANCE_ID$(NC)"; \
		EC2_PUBLIC_IP=$$(cd $(TERRAFORM_DIR) && terraform output -raw ec2_public_ip 2>/dev/null || echo ""); \
		EC2_PRIVATE_IP=$$(cd $(TERRAFORM_DIR) && terraform output -raw ec2_private_ip 2>/dev/null || echo ""); \
		ALB_DNS=$$(cd $(TERRAFORM_DIR) && terraform output -raw load_balancer_dns 2>/dev/null || echo ""); \
		APP_URL=$$(cd $(TERRAFORM_DIR) && terraform output -raw application_url 2>/dev/null || echo ""); \
		echo "$(GREEN)Public IP: $$EC2_PUBLIC_IP$(NC)"; \
		echo "$(GREEN)Private IP: $$EC2_PRIVATE_IP$(NC)"; \
		echo "$(GREEN)Load Balancer: $$ALB_DNS$(NC)"; \
		echo "$(GREEN)Application URL: $$APP_URL$(NC)"; \
		aws ec2 describe-instances --region $(AWS_REGION) --instance-ids "$$EC2_INSTANCE_ID" \
			--query 'Reservations[0].Instances[0].{State:State.Name,Type:InstanceType,LaunchTime:LaunchTime}' \
			--output table 2>/dev/null || echo "$(YELLOW)Instance details not available$(NC)"; \
	fi

ec2-ssh: check-env check-aws ## SSH into EC2 instance
	@echo "$(BLUE)Connecting to EC2 instance for $(ENV)...$(NC)"
	@EC2_PUBLIC_IP=$$(cd $(TERRAFORM_DIR) && terraform output -raw ec2_public_ip); \
	if [ -z "$$EC2_PUBLIC_IP" ] || [ "$$EC2_PUBLIC_IP" = "null" ]; then \
		echo "$(RED)Error: EC2 instance not found. Run 'make ec2-deploy' first.$(NC)"; \
		exit 1; \
	fi; \
	echo "$(BLUE)Connecting to $$EC2_PUBLIC_IP...$(NC)"; \
	ssh -o StrictHostKeyChecking=no ec2-user@$$EC2_PUBLIC_IP

ec2-logs: check-env ec2-check ## Show application logs from EC2
	@echo "$(BLUE)Fetching application logs from EC2 for $(ENV)...$(NC)"
	@uv run ansible -i infra/ansible/inventory/$(ENV).yml dbmcp -m shell -a "docker compose -f /opt/dbmcp/docker-compose.yml logs --tail=50" -b

## Information
info: ## Show current configuration
	@echo "$(BLUE)Current Configuration:$(NC)"
	@echo "Environment: $(ENV)"
	@echo "AWS Region: $(AWS_REGION)"
	@echo "Image Tag: $(IMAGE_TAG)"
	@echo "Config File: $(CONFIG_FILE)"
	@echo "Terraform Dir: $(TERRAFORM_DIR)"
	@if [ -n "$(ECR_REPOSITORY_URL)" ]; then \
		echo "ECR Repository: $(ECR_REPOSITORY_URL)"; \
	fi

status: terraform-output ec2-status ## Show complete deployment status 