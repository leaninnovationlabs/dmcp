# DBMCP - Database Backend Server

A Python backend server built with FastAPI that can connect to various databases and run queries. The server provides APIs for managing datasources, creating named queries, and executing queries with parameter support and pagination.

## Features

- **Datasource Management**: Create and manage database connections for various database types
- **Named Queries**: Store and manage parameterized queries
- **Query Execution**: Run queries with parameter support and pagination
- **Multiple Database Support**: PostgreSQL, MySQL, SQLite
- **Password Encryption**: Database passwords are encrypted using Fernet symmetric encryption
- **MCP Tool Support**: Expose functionality as MCP tools

## Setup

1. Install dependencies using uv:
```bash
uv sync
```

2. Initialize the database:
```bash
python manage_db.py init
```

3. Run the development server:
```bash
uv run uvicorn app.main:app --reload
```

4. Access the API documentation at: http://localhost:8000/docs

## Database Management

This project uses **Alembic** for database schema management. All database changes are handled through migrations to ensure version control and safe schema evolution.

### Quick Start

```bash
# Initialize database (creates tables)
python manage_db.py init

# Check migration status
python manage_db.py status

# Apply pending migrations
python manage_db.py upgrade
```

### Available Commands

| Command | Description |
|---------|-------------|
| `python manage_db.py init` | Initialize database with initial schema |
| `python manage_db.py upgrade` | Apply all pending migrations |
| `python manage_db.py downgrade <revision>` | Downgrade to specific revision |
| `python manage_db.py revision -m "message"` | Create new migration |
| `python manage_db.py status` | Show current migration status |
| `python manage_db.py history` | Show migration history |
| `python manage_db.py reset` | Reset database (⚠️ deletes all data) |

### Creating New Migrations

When you modify the database models in `app/models/database.py`, create a new migration:

```bash
# Create migration for model changes
python manage_db.py revision -m "Add new column to users table"

# Review the generated migration file in alembic/versions/
# Then apply the migration
python manage_db.py upgrade
```

### Manual Alembic Commands

You can also use Alembic commands directly:

```bash
# Create migration
alembic revision --autogenerate -m "Description of changes"

# Apply migrations
alembic upgrade head

# Downgrade
alembic downgrade -1

# Check status
alembic current
alembic history
```

### Database Schema

The current schema includes:

- **datasources** table: Stores database connection configurations
- **queries** table: Stores named queries with parameters

See `app/models/database.py` for the complete model definitions.

## API Endpoints

- `POST /datasources` - Create a new datasource
- `GET /datasources` - List all datasources
- `GET /datasources/{id}` - Get a specific datasource
- `DELETE /datasources/{id}` - Delete a datasource

- `POST /queries` - Create a new named query
- `GET /queries` - List all queries
- `GET /queries/{id}` - Get a specific query
- `DELETE /queries/{id}` - Delete a query

- `POST /execute/{query_id}` - Execute a named query with parameters
- `POST /execute/raw` - Execute a raw SQL query

## Environment Variables

Create a `.env` file with:
```
DATABASE_URL=sqlite:///./dbmcp.db
SECRET_KEY=your-secret-key-here-change-this-in-production
```

**Important**: The `SECRET_KEY` is used for password encryption. Make sure to use a strong, unique secret key in production and keep it secure.



----

GET      /health                        Health Check
GET      /datasources/                  List Datasources
POST     /datasources/                  Create Datasource
GET      /datasources/{datasource_id}   Get Datasource
DELETE   /datasources/{datasource_id}   Delete Datasource
GET      /queries/                      List Queries
POST     /queries/                      Create Query
GET      /queries/{query_id}            Get Query
DELETE   /queries/{query_id}            Delete Query
POST     /execute/{query_id}            Execute Named Query
POST     /execute/raw                   Execute Raw Query