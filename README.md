# DBMCP - Database Backend Server

A lightweight database backend server with FastAPI and MCP (Model Context Protocol) support for managing database connections and executing configurable SQL tools.

## Quick Start

### Local Development
```bash
# Install dependencies
make install

# Start with Docker Compose (recommended)
docker-compose up

# Access the web UI
open http://localhost:8000/dbmcp/ui/
```

### RDS Test Database
Create a test RDS instance with sample boat parts warehouse data:

```bash
# Create RDS test instance and run migrations
make rds-test-up ENV=development

# Check status
make rds-test-status ENV=development

# Get connection info
make rds-test-connect ENV=development

# Destroy when done
make rds-test-down ENV=development
```

## Architecture

**Dual Server Design:**
- **FastAPI Server** (port 8000): REST API + Web UI for database tool management
- **MCP Server** (port 4200): MCP protocol server for dynamic tool execution

**Key Features:**
- Dynamic SQL tool registration and execution
- Multi-database support (PostgreSQL, MySQL)
- Jinja2 template support for parameterized queries
- JWT authentication and authorization
- Enterprise-grade Len Silverston dimensional warehouse schema

## Development Commands

```bash
# Code quality
make format          # Format code with black/isort
make lint            # Run linters
make test            # Run tests

# Local development  
make docker-dev      # Run with live reload
make token           # Generate JWT token for API auth

# Build and deploy
make build ENV=development
make deploy ENV=development
```

## Configuration

Environment-specific configs in `infra/config/`:
- `development.yml` - Local development
- `staging.yml` - Staging environment  
- `production.yml` - Production environment

## Database Schema

The test RDS instance includes an enterprise-grade boat parts warehouse schema following Len Silverston's dimensional modeling methodology:

- **Party Management**: Universal party model for customers, suppliers, manufacturers
- **Product Catalog**: Hierarchical product categories with boat compatibility
- **Inventory Management**: Multi-location inventory tracking with lot/serial numbers
- **Order Management**: Complete order lifecycle with status tracking
- **Facility Management**: Warehouse and retail location management

Sample data includes realistic boat parts from major manufacturers (Mercury, Yamaha, Brunswick) with proper inventory levels and pricing.

## API Authentication

Generate a JWT token for API access:
```bash
make token
```

Use the token in the Authorization header:
```bash
curl -H "Authorization: Bearer <token>" http://localhost:8000/dbmcp/api/...
```

## Infrastructure

- **Terraform**: AWS infrastructure (EKS, ECR, RDS)
- **Helm**: Kubernetes deployments
- **Docker**: Multi-stage builds with UV package manager
- **Alembic**: Database migrations (separate for app and warehouse schemas)