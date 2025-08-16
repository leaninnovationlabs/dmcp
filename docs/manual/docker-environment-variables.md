# Docker Environment Variables Configuration

This document explains how to configure environment variables when running the DBMCP application in Docker.

## Overview

The DBMCP application uses several environment variables for configuration. When running in Docker, you have multiple options to pass these variables to the container.

## Environment Variables Reference

Based on `env.example`, here are the key environment variables:

### Database Configuration
- `DATABASE_URL`: Database connection string (default: `sqlite+aiosqlite:///./dbmcp.db`)

### Security
- `SECRET_KEY`: Secret key for the application (change in production)
- `JWT_SECRET_KEY`: JWT signing secret (change in production)
- `JWT_ALGORITHM`: JWT algorithm (default: `HS256`)
- `JWT_EXPIRATION_MINUTES`: JWT token expiration time (default: `60`)

### Server Configuration
- `HOST`: Server host (default: `0.0.0.0`)
- `PORT`: Server port (default: `8000`)
- `DEBUG`: Debug mode (default: `true`)
- `LOG_LEVEL`: Logging level (default: `INFO`)

### CORS Configuration
- `ALLOWED_ORIGINS`: List of allowed CORS origins

### MCP Server Configuration
- `MCP_TRANSPORT`: MCP transport type (default: `stdio`)
- `MCP_HOST`: MCP host (default: `127.0.0.1`)
- `MCP_PORT`: MCP port (default: `4200`)
- `MCP_PATH`: MCP path (default: `/dbmcp`)
- `MCP_LOG_LEVEL`: MCP logging level (default: `debug`)

## Method 1: Using Docker Compose (Recommended)

The easiest way to run with environment variables is using the provided `docker-compose.yml`:

```bash
# Start the application
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the application
docker-compose down
```

### Customizing Environment Variables in Docker Compose

Edit the `docker-compose.yml` file and modify the `environment` section:

```yaml
environment:
  - DATABASE_URL=postgresql://user:password@host:5432/dbname
  - SECRET_KEY=your-custom-secret-key
  - DEBUG=false
  - LOG_LEVEL=WARNING
```

## Method 2: Using Environment File with Docker Compose

1. Create a `.env` file in your project directory:
```bash
cp env.example .env
# Edit .env with your values
```

2. Uncomment the `env_file` section in `docker-compose.yml`:
```yaml
env_file:
  - .env
```

3. Run with Docker Compose:
```bash
docker-compose up -d
```

## Method 3: Direct Docker Run Command

### Option A: Individual Environment Variables

```bash
docker run -d \
  --name dbmcp \
  -p 8000:8000 \
  -e DATABASE_URL="sqlite+aiosqlite:///./dbmcp.db" \
  -e SECRET_KEY="your-secret-key" \
  -e JWT_SECRET_KEY="your-jwt-secret" \
  -e DEBUG="false" \
  -e LOG_LEVEL="WARNING" \
  -v $(pwd)/dbmcp.db:/app/dbmcp.db \
  dbmcp:latest
```

### Option B: Environment File

1. Create a `.env` file:
```bash
cp env.example .env
# Edit .env with your values
```

2. Run with `--env-file`:
```bash
docker run -d \
  --name dbmcp \
  -p 8000:8000 \
  --env-file .env \
  -v $(pwd)/dbmcp.db:/app/dbmcp.db \
  dbmcp:latest
```

## Method 4: Shell Environment Variables

Export variables in your shell and use them:

```bash
export DATABASE_URL="postgresql://user:pass@host:5432/db"
export SECRET_KEY="my-secret-key"
export DEBUG="false"

docker run -d \
  --name dbmcp \
  -p 8000:8000 \
  -e DATABASE_URL \
  -e SECRET_KEY \
  -e DEBUG \
  -v $(pwd)/dbmcp.db:/app/dbmcp.db \
  dbmcp:latest
```

## Production Considerations

### Security
- **Always change default secret keys** in production
- Use strong, randomly generated secrets
- Consider using Docker secrets for sensitive data in production environments

### Database
- For production, use a proper database (PostgreSQL, MySQL) instead of SQLite
- Ensure database credentials are properly secured

### Environment-Specific Configs
Create different environment files for different environments:

```bash
# Development
cp env.example .env.dev

# Production
cp env.example .env.prod

# Staging
cp env.example .env.staging
```

## Troubleshooting

### Check Environment Variables in Running Container

```bash
# List all environment variables
docker exec dbmcp env

# Check specific variable
docker exec dbmcp sh -c 'echo $DATABASE_URL'
```

### View Application Logs

```bash
# Docker Compose
docker-compose logs -f

# Direct Docker
docker logs -f dbmcp
```

### Common Issues

1. **Database Connection Errors**: Check `DATABASE_URL` format and connectivity
2. **Permission Denied**: Ensure database file is writable by the container
3. **Port Already in Use**: Change the port mapping in Docker run/compose

## Examples

### Development Setup
```bash
# Quick start with defaults
docker-compose up -d

# Custom development config
docker run -d \
  --name dbmcp-dev \
  -p 8000:8000 \
  -e DEBUG=true \
  -e LOG_LEVEL=DEBUG \
  -v $(pwd)/dbmcp.db:/app/dbmcp.db \
  dbmcp:latest
```

### Production Setup
```bash
docker run -d \
  --name dbmcp-prod \
  -p 8000:8000 \
  -e DATABASE_URL="postgresql://user:pass@db:5432/dbmcp" \
  -e SECRET_KEY="$(openssl rand -hex 32)" \
  -e JWT_SECRET_KEY="$(openssl rand -hex 32)" \
  -e DEBUG=false \
  -e LOG_LEVEL=WARNING \
  --restart unless-stopped \
  dbmcp:latest
```

## Next Steps

1. Choose the method that best fits your workflow
2. Create your environment configuration
3. Start the container
4. Access the application at `http://localhost:8000`
5. Check the logs to ensure everything is working correctly
