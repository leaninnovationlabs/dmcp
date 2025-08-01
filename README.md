# DBMCP - Database Backend Server

A Python backend server built with FastAPI that can connect to various databases and run queries. The server provides APIs for managing datasources, creating named queries, and executing queries with parameter support and pagination.

## Features
- **Datasource Management**: Ability to connect to various databases
- **Named Queries**: Store and manage parameterized queries with jinja template support
- **Query Execution**: Run queries with parameter support and pagination
- **Multiple Database Support**: PostgreSQL, MySQL, SQLite, and more coming soon
- **MCP Tool Support**: Expose APIs as MCP tools
- **Authentication**: Support for bearer token authentication
- **UI**: A simple UI for managing datasources and queries

## Setup

1. Install dependencies using uv:
```bash
uv sync
```

2. Initialize the database:
```bash
uv run alembic upgrade head
```

3. Run the API server:
```bash
uv run api_run.py
```

4. Access the API documentation at: http://localhost:8000/dbmcp/docs

5. Access the UI at: http://localhost:8000/dbmcp/ui

## MCP Server Setup
This project also provides an MCP (Model Context Protocol) server that exposes database operations as tools for AI assistants. By default MCP server runs on port 4200 with /dbmcp/mcp prefix

1. Starting the MCP Server

```bash
# Start the MCP server
uv run mcp_run.py
```

2. Launch MCP Inspector:

```bash
npx @modelcontextprotocol/inspector
```

- Provide the URL as http://127.0.0.1:4200/dbmcp
- Set the Header Name as Authorization
- Set the Header Value as Bearer <token> (replace <token> with the token you generated in Token Handling section)

3. Using with MCP Clients with stdio transport
This will disable the authentication and allow the MCP client to access the APIs directly. 
**Do not use this in production.**

**Claude Desktop**: Add the following to your `claude_desktop_config.json`:
```json
{
    "mcpServers": {
        "dbmcp": {
            "command": "<uv_path>",
            "args": [
                "--directory",
                "<source_path>/dbmcp",
                "run",
                "mcp_run.py"
            ],
            "env": {
                "TRANSPORT": "stdio"
            }
        }
    }
}
```

## Token Handling

Support for bearer token authentication is built in. To create a token, run the following command:

```bash
uv run scripts/apptoken.py
```

## Database Management

This project uses **Alembic** for database schema management. All database changes are handled through migrations to ensure version control and safe schema evolution.

## Database Schema Management

You can also use Alembic commands directly:

```bash
# Create migration
uv run alembic revision --autogenerate -m "Description of changes"

# Apply migrations
uv run alembic upgrade head

# Downgrade
uv run alembic downgrade -1

# Check status
uv run alembic current
uv run alembic history
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

**Important**: 
- The `SECRET_KEY` is used for database password encryption. Make sure to use a strong, unique secret key in production and keep it secure.
- The `JWT_SECRET_KEY` is used for JWT token generation. Make sure to use a strong, unique secret key in production and keep it secure.


## API Documentation

All routes are automatically documented in the OpenAPI schema and available at:
- **Swagger UI**: http://localhost:8000/dbmcp/docs
- **ReDoc**: http://localhost:8000/dbmcp/redoc
- **OpenAPI JSON**: http://localhost:8000/dbmcp/openapi.json 


**Authentication Usage:**
- **Web UI**: Enter the generated token in the authentication modal when prompted
- **API Client**: Include the token in your request headers or authentication settings
- **MCP Inspector**: Specify the token in the "Bearer Token" field in the authentication section


# TOOD
- Do more testing for various datasources and complex queries and parameters (generate test cases)
- Tool with param not working from inspector
- Not detecting the new tools from the inspector, see how to list out the get tools
- No proper error handling when the response does not have valid results or errors out
