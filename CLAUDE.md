# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

DBMCP is a lightweight database backend server with FastAPI and MCP (Model Context Protocol) support. It provides a dual-architecture solution:

1. **FastAPI Server** (`app/main.py`) - REST API with web UI for database tool management
2. **MCP Server** (`app/mcp_server.py`) - MCP protocol server for dynamic tool execution

The application manages database connections and executes configurable SQL tools/queries through both REST endpoints and MCP tools.

## Development Commands

### Environment Setup
```bash
# Install dependencies
make install
# or
uv sync --dev

# Generate JWT token for API authentication
make token
# or
uv run scripts/apptoken.py
```

### Code Quality
```bash
# Format code
make format
uv run black app/
uv run isort app/

# Lint code
make lint
uv run black --check app/
uv run isort --check-only app/
uv run flake8 app/

# Run tests
make test
uv run pytest tests/ -v
```

### Local Development
```bash
# Run with Docker Compose (recommended for full stack)
docker-compose up

# Run FastAPI server locally
uv run python api_run.py

# Run MCP server locally  
uv run python mcp_run.py

# Development mode with live reload
make docker-dev
```

### Build and Deploy
```bash
# Build Docker images
make build ENV=development

# Deploy to specific environment
make deploy ENV=development
make deploy ENV=staging  
make deploy ENV=production

# Helm deployment
make helm-deploy ENV=development
```

## Architecture

### Dual Server Architecture
- **FastAPI Server** (port 8000): Web UI, REST API, database management
- **MCP Server** (port 4200): MCP protocol for dynamic tool registration and execution
- **AWS Aurora Serverless v2**: Primary database for tool configurations and data
- **RDS Test Instance**: Optional test database with Len Silverston warehouse schema

### Key Components

**Database Layer** (`app/database.py`):
- SQLAlchemy async setup with connection pooling
- Alembic migrations in `alembic/versions/`

**Services** (`app/services/`):
- `ToolService`: CRUD operations for database tools
- `ToolExecutionService`: Executes SQL queries with parameter substitution
- `JinjaTemplateService`: Template rendering for dynamic queries

**MCP Integration** (`app/mcp_server.py`):
- Dynamic tool registration from database configurations
- FastMCP server with HTTP transport support
- Authentication and logging middleware

**Data Sources** (`app/datasources/`):
- Support for PostgreSQL, MySQL
- Connection management and query execution
- Jinja2 template support for dynamic queries

### Configuration Management
- Environment-based config in `infra/config/` (development.yml, staging.yml, production.yml)
- AWS Parameter Store integration for sensitive values
- JWT authentication with configurable secrets

### Current Infrastructure Setup
- **Aurora Serverless v2**: `dbmcp-development.cluster-cfyuw4cq2vh5.us-east-1.rds.amazonaws.com` (main database)
- **Parameter Store**: `/development/dbmcp/database_url` contains Aurora connection string
- **RDS Test Instance**: `dbmcp-test-development.cfyuw4cq2vh5.us-east-1.rds.amazonaws.com` (warehouse schema)
- **Known Issue**: MCP deployment currently hardcoded to wrong database URL instead of using Parameter Store

### Infrastructure
- **Docker**: Multi-stage builds with UV package manager
- **Terraform**: AWS EKS deployment with ECR
- **Helm**: Kubernetes deployment charts
- **Nginx**: Reverse proxy configuration

## Database Migrations

```bash
# Create migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Check current version
alembic current
```

## Environment Variables

Key settings (see `app/core/config.py`):
- `DATABASE_URL`: PostgreSQL connection string
- `JWT_SECRET_KEY`: JWT token signing key
- `TRANSPORT`: MCP transport mode ("stdio" or "http")
- `USE_PARAMETER_STORE`: Enable AWS Parameter Store for config
- CORS settings for cross-origin requests

## Testing and Quality

The project uses:
- **pytest** with async support for testing
- **black** for code formatting (line length: 88)
- **isort** for import sorting (black profile)
- **flake8** for linting
- **mypy** for type checking (strict mode)

## Deployment Environments

Environment-specific configurations in `infra/config/`:
- `development.yml`: Local development
- `staging.yml`: Staging environment  
- `production.yml`: Production environment

Use `ENV=environment_name` with make commands to target specific environments.