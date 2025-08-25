# DMCP - Data Model Context Protocol

A Python backend server built with FastAPI that can connect to any data source via query, API, or code and expose data operations as MCP tools for AI assistants. The server provides APIs for managing datasources, creating named operations, and executing operations with parameter support and pagination.

You can find the documentation [here](https://dmcp.opsloom.io/)

## Features
- **Datasource Management**: Ability to connect to various data sources
- **Named Operations**: Store and manage parameterized operations with jinja template support
- **Operation Execution**: Run operations with parameter support and pagination
- **Multiple Data Source Support**: PostgreSQL, MySQL, SQLite, Databricks, APIs, and more coming soon
- **MCP Tool Support**: Expose data operations as MCP tools
- **Authentication**: Support for bearer token authentication
- **UI**: A simple UI for managing datasources and operations

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
 
  **Option B: .env File**
  Copy `env.example` to `.env` and set MCP_TRANSPORT to `stdio` or `http`
  ```bash
  cp env.example .env
  ```


3. Initialize the database:
```bash
  uv run alembic upgrade head
```

4. Run the API server, MCP server and UI:
```bash
  uv run main.py
```

4. Access the UI at: http://localhost:8000/dmcp/ui


## MCP Server Setup
This project also provides an MCP (Model Context Protocol) server that exposes data operations as tools for AI assistants. By default MCP server runs on port 8000 with /dmcp/mcp prefix

1. Launch MCP Inspector:

```bash
npx @modelcontextprotocol/inspector
```

- Provide the URL as http://127.0.0.1:8000/dmcp
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
  --name dmcp \
  -p 8000:8000 \
  -e DATABASE_URL="sqlite+aiosqlite:///./dmcp.db" \
  -e SECRET_KEY="your-secret-key" \
  -e LOG_LEVEL="WARNING" \
  -v $(pwd)/dmcp.db:/app/dmcp.db \
  dmcp:latest

```


### Using Docker Compose

The `docker-compose.yml` file is already configured with environment variables:

```bash
# Start with default settings
docker-compose up -d

# Or override with custom port
docker-compose up -d -e PORT=8000
```

## Environment Variables

Create a `.env` file with required variables. Checkout `.env.example` file for reference. Only SECRET_KEY is required. Here are all the available configuration options:

### Example .env file
```bash
# Database Configuration
DATABASE_URL=sqlite+aiosqlite:///./dmcp.db

# Security
SECRET_KEY=your-super-secret-key-here
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

## API Documentation

All routes are automatically documented in the OpenAPI schema and available at:
- **Swagger UI**: http://localhost:8000/dmcp/docs
- **ReDoc**: http://localhost:8000/dmcp/redoc
- **OpenAPI JSON**: http://localhost:8000/dmcp/openapi.json 

**Authentication Usage:**
- **Web UI**: Enter the generated token in the authentication modal when prompted
- **API Client**: Include the token in your request headers or authentication settings
- **MCP Inspector**: Specify the token in the "Bearer Token" field in the authentication section
