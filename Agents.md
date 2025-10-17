# Backend Cursor Rules for DMCP FastAPI Application

## Important: Running the Application

**Always use `uv` to run commands in this project:**
- Start the server: `uv run main.py`
- Run Alembic migrations: `uv run alembic upgrade head`
- Run tests: `uv run pytest`
- DO NOT use `python` directly, always use `uv run`

## Technology Stack
- Python 3.10+ with FastAPI
- SQLAlchemy 2.0+ for ORM
- Alembic for database migrations
- Pydantic for data validation and serialization
- JWT for authentication
- Multiple database support (PostgreSQL, MySQL, SQLite, Databricks)
- MCP (Model Context Protocol) integration

## Project Structure
- `app/` - Main application package
- `app/core/` - Core functionality (config, auth, encryption)
- `app/models/` - Database models and schemas
- `app/routes/` - API route handlers
- `app/services/` - Business logic layer
- `app/repositories/` - Data access layer
- `app/datasources/` - Database connection adapters
- `app/mcp/` - MCP server implementation

## Code Organization Guidelines

### File Structure
- Follow the layered architecture pattern
- Keep routes thin - delegate to services
- Services contain business logic
- Repositories handle data access
- Models define data structures
- Use dependency injection for testability

### Import Organization
1. Standard library imports
2. Third-party library imports
3. Local application imports
4. Type-only imports at the end

Example:
```python
import os
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.config import settings
from app.services.user_service import UserService
from app.models.schemas import UserCreate, UserResponse
```

## API Development Guidelines

### Route Design
- Use RESTful conventions
- Group related endpoints in routers
- Use proper HTTP status codes
- Implement proper error handling
- Use dependency injection for database sessions
- Add proper authentication where needed

### Request/Response Models
- Use Pydantic models for all request/response validation
- Define clear schemas in `app/models/schemas.py`
- Use proper field validation and constraints
- Include proper documentation strings
- Use type hints throughout

### Error Handling
- Use custom exceptions from `app/core/exceptions.py`
- Return proper HTTP status codes
- Provide meaningful error messages
- Log errors appropriately
- Use try-catch blocks for external service calls

## Database Guidelines

### Models
- Use SQLAlchemy 2.0+ syntax
- Define models in `app/models/database.py`
- Use proper relationships and constraints
- Include proper indexes
- Use Alembic for all schema changes

### Migrations
- Always create migrations for schema changes
- Use descriptive migration names
- Test migrations on development data
- Never edit existing migration files

### Queries
- Use repository pattern for data access
- Implement proper error handling
- Use transactions for multi-step operations
- Avoid N+1 query problems
- Use proper indexing strategies

## Authentication & Security

### JWT Implementation
- Use proper token validation
- Implement token refresh mechanisms
- Store tokens securely
- Use proper expiration times
- Validate all incoming requests

### Password Security
- Use bcrypt for password hashing
- Implement proper salt generation
- Never store plain text passwords
- Use strong password requirements

### Data Encryption
- Use proper encryption for sensitive data
- Implement key rotation strategies
- Use secure random generation
- Protect against common vulnerabilities

## Service Layer Guidelines

### Business Logic
- Keep services focused on business logic
- Use dependency injection
- Implement proper error handling
- Use async/await for I/O operations
- Keep services testable

### Data Validation
- Validate all input data
- Use Pydantic for validation
- Implement proper sanitization
- Check for SQL injection vulnerabilities
- Validate file uploads properly

## MCP Integration

### Tool Implementation
- Follow MCP protocol specifications
- Implement proper tool registration
- Use proper error handling
- Provide clear tool descriptions
- Implement proper authentication

### Middleware
- Use middleware for cross-cutting concerns
- Implement proper logging
- Add authentication middleware
- Use proper error handling middleware

## Code Quality Standards

### Type Hints
- Use type hints for all function parameters and return values
- Use proper generic types
- Use Union types for multiple possible types
- Use Optional for nullable values
- Use proper typing for async functions

### Documentation
- Use docstrings for all public functions and classes
- Follow Google docstring format
- Include parameter descriptions
- Include return value descriptions
- Include example usage where helpful

### Testing
- Write unit tests for all services
- Test API endpoints with proper test data
- Use pytest and pytest-asyncio
- Mock external dependencies
- Test error conditions

### Code Style
- Follow PEP 8 guidelines
- Use Black for code formatting
- Use isort for import sorting
- Use flake8 for linting
- Use mypy for type checking

## Environment Configuration

### Settings Management
- Use Pydantic Settings for configuration
- Use environment variables for secrets
- Provide sensible defaults
- Use proper validation
- Document all configuration options

## Logging and Monitoring

### Logging
- Use structured logging
- Log important business events
- Include proper context information
- Use appropriate log levels
- Implement proper log rotation

### Error Tracking
- Implement proper error tracking
- Include stack traces
- Add request context
- Monitor performance metrics
- Set up proper alerting

## Security Best Practices

### Input Validation
- Validate all input data
- Use proper sanitization
- Implement CSRF protection
- Use proper CORS configuration
- Validate file uploads

### Authentication
- Implement proper session management
- Use secure token storage
- Implement proper logout
- Use HTTPS in production
- Implement proper rate limiting

### Data Protection
- Encrypt sensitive data
- Use proper access controls
- Implement audit logging
- Follow data retention policies
- Comply with privacy regulations
