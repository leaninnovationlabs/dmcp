# Docker Compose Deployment

This directory contains the Docker Compose configuration for deploying DMCP, WURF, and PostgreSQL services.

## Prerequisites

Before starting the services, ensure you have the following Docker images built:

- **dmcp:latest** - DMCP application image
- **wurf:latest** - WURF application image
- **pgvector/pgvector:pg16-trixie** - PostgreSQL with pgvector extension (automatically pulled)

## Environment Files

Each service requires its own environment file. Create the following files in this directory:

### 1. `.env.db` - PostgreSQL Configuration
Contains database configuration variables for the PostgreSQL service.

### 2. `.env.dmcp` - DMCP Application Configuration
Contains environment variables for the DMCP application service.

### 3. `.env.wurf` - WURF Application Configuration
Contains environment variables for the WURF application service.

## Starting Services

To bring up all services:

```bash
docker-compose up -d
```

The `-d` flag runs containers in detached mode (background).

## Stopping Services

To bring down all services:

```bash
docker-compose down
```

To also remove volumes (⚠️ this will delete database data):

```bash
docker-compose down -v
```

## Services

- **postgres** - PostgreSQL database with pgvector extension
- **dmcp** - DMCP application (port 8000)
- **wurf** - WURF application (port 8080)

## Viewing Logs

View logs for all services:
```bash
docker-compose logs -f
```

View logs for a specific service:
```bash
docker-compose logs -f dmcp
docker-compose logs -f wurf
docker-compose logs -f postgres
```

## Image Names

The docker-compose file references the following Docker images:

- `dmcp:latest` - DMCP application
- `wurf:latest` - WURF application
- `pgvector/pgvector:pg16-trixie` - PostgreSQL with pgvector extension

Ensure these images are built and available before starting the services.

