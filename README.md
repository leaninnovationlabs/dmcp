# DBMCP - Database Backend Server

A Python backend server built with FastAPI that can connect to various databases and run queries. The server provides APIs for managing datasources, creating named queries, and executing queries with parameter support and pagination.

You can find the documentation [here](https://dev-dbmcp.opsloom.io/)

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

2. **Configure SECRET_KEY** (Required):
   The application requires a secure SECRET_KEY to be set. This is used for JWT token signing and other security features.
   
   **Option A: Environment Variable**
   ```bash
   export SECRET_KEY="your-secure-secret-key-here"
   ```
   
   **Important**: The SECRET_KEY must be:
   - At least 32 characters long
   - Not a placeholder value
   - Kept secret and secure

3. Initialize the database:
```bash
uv run alembic upgrade head
```

4. Run the API server, MCP server and UI:
```bash
uv run main.py
```

4. Access the API documentation at: http://localhost:8000/dbmcp/docs

5. Access the UI at: http://localhost:8000/dbmcp/ui

## MCP Server Setup
This project also provides an MCP (Model Context Protocol) server that exposes database operations as tools for AI assistants. By default MCP server runs on port 8000 with /dbmcp/mcp prefix

1. Launch MCP Inspector:

```bash
npx @modelcontextprotocol/inspector
```

- Provide the URL as http://127.0.0.1:8000/dbmcp
- Set the Header Name as Authorization
- Set the Header Value as Bearer <token> (replace <token> with the token you generated in Token Handling section)


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

## Docker

### Quick Start with Docker

Build and run the container:

```bash
# Build the image
make docker-build

# Run on default port 8000
make docker-run

or 

docker run -d \
  --name dbmcp \
  -p 8000:8000 \
  -e DATABASE_URL="sqlite+aiosqlite:///./dbmcp.db" \
  -e SECRET_KEY="your-secret-key" \
  -e LOG_LEVEL="WARNING" \
  -v $(pwd)/dbmcp.db:/app/dbmcp.db \
  dbmcp:latest

```


### Using Docker Compose

The `docker-compose.yml` file is already configured with environment variables:

```bash
# Start with default settings
docker-compose up -d

# Or override with custom port
docker-compose up -d -e PORT=7000
```

## Environment Variables

Create a `.env` file with required variables. Checkout `.env.example` file for reference. Here are all the available configuration options:

### Database Configuration
- `DATABASE_URL`: Database connection string (default: `sqlite+aiosqlite:///./dbmcp.db`)
  - Supports SQLite, PostgreSQL, MySQL, and other databases
  - Format: `postgresql://user:password@host:port/database` or `mysql://user:password@host:port/database`

### Security
- `SECRET_KEY`: Secret key for database password encryption (required)
  - **Important**: Use a strong, unique secret key in production and keep it secure
  - Used for encrypting sensitive datasource credentials

### JWT Configuration
- `JWT_SECRET_KEY`: Secret key for JWT token generation (required)
  - **Important**: Use a strong, unique secret key in production and keep it secure
  - Should be different from the main SECRET_KEY
- `JWT_ALGORITHM`: JWT signing algorithm (default: `HS256`)
- `JWT_EXPIRATION_MINUTES`: Token expiration time in minutes (default: `60`)

### Server Configuration
- `HOST`: Server host address (default: `0.0.0.0`)
- `PORT`: Server port number (default: `8000`)
- `DEBUG`: Enable debug mode (default: `true`)

### Logging
- `LOG_LEVEL`: Logging level (default: `INFO`)
  - Options: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`

### CORS Configuration
- `ALLOWED_ORIGINS`: List of allowed origins for CORS (default: `["http://localhost:3000", "http://localhost:8000"]`)
  - Add your frontend URL if served from a different port/domain
  - Format: JSON array of URLs

### MCP Server Configuration
- `MCP_TRANSPORT`: MCP transport type (default: `stdio`)
  - Options: `stdio` (for local MCP clients), `http` (for remote clients)
- `MCP_HOST`: MCP server host (default: `127.0.0.1`)
- `MCP_PORT`: MCP server port (default: `8000`)
- `MCP_PATH`: MCP server path prefix (default: `/dbmcp`)
- `MCP_LOG_LEVEL`: MCP server logging level (default: `debug`)

### Example .env file
```bash
# Database Configuration
DATABASE_URL=postgresql://user:password@localhost:5432/dbmcp

# Security
SECRET_KEY=your-super-secret-key-here

# Server Configuration
HOST=0.0.0.0
PORT=8000
DEBUG=false

# Logging
LOG_LEVEL=INFO

# CORS
ALLOWED_ORIGINS=["http://localhost:3000", "https://yourdomain.com"]

# MCP Server
MCP_TRANSPORT=http
MCP_HOST=0.0.0.0
MCP_PORT=8000
```

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

## API Documentation

All routes are automatically documented in the OpenAPI schema and available at:
- **Swagger UI**: http://localhost:8000/dbmcp/docs
- **ReDoc**: http://localhost:8000/dbmcp/redoc
- **OpenAPI JSON**: http://localhost:8000/dbmcp/openapi.json 

**Authentication Usage:**
- **Web UI**: Enter the generated token in the authentication modal when prompted
- **API Client**: Include the token in your request headers or authentication settings
- **MCP Inspector**: Specify the token in the "Bearer Token" field in the authentication section

# TODO
Bugs:
- Not detecting the new tools from the inspector, see how to list out the get tools

Cleanup:
- Fix the error message response from the MCP server
- Make sure we are not throwing the sql in the errors {{server}}/datasources create is doing this
- Tool with param not working from inspector
- No proper error handling when the response does not have valid results or errors out
