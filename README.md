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

2. Run the development server:
```bash
uv run uvicorn app.main:app --reload
```

3. Access the API documentation at: http://localhost:8000/docs

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