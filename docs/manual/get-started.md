---
outline: deep
---

# Installation & Setup

This guide will walk you through installing and setting up DBMCP on your system.

## Prerequisites

Before installing DBMCP, ensure you have:

- **Python 3.10 or higher**
- **uv package manager** (recommended) or pip
- **Git** (for cloning the repository)

### Installing uv (Recommended)

uv is a fast Python package installer and resolver, written in Rust. It's the recommended way to manage dependencies for this project.

```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Or using pip
pip install uv
```

## Installation Steps

### 1. Clone the Repository

```bash
git clone <repository-url>
cd dbmcp
```

### 2. Install Dependencies

Using uv (recommended):
```bash
uv sync
```

Or using pip:
```bash
pip install -r requirements.txt
```

### 3. Environment Configuration

Create a `.env` file in the project root:

```bash
cp env.example .env
```

Edit the `.env` file with your configuration:

```env
# Database Configuration
DATABASE_URL=sqlite+aiosqlite:///./dbmcp.db

# Security (IMPORTANT: Change these in production!)
SECRET_KEY=your-secret-key-here-change-this-in-production
JWT_SECRET_KEY=jwt-secret-key-change-this-in-production

# Server Configuration
HOST=0.0.0.0
PORT=8000
DEBUG=true

# Logging
LOG_LEVEL=INFO

# CORS (add your frontend URLs)
ALLOWED_ORIGINS=["http://localhost:3000", "http://localhost:8000"]
```

### 4. Initialize the Database

```bash
uv run alembic upgrade head
```

### 5. Generate Authentication Token

Create a token for API access:

```bash
uv run scripts/apptoken.py
```

This will output a token that you'll use for authentication.

### 6. Start the Server

#### API Server
```bash
uv run api_run.py
```

The API server will be available at:
- **API Documentation**: http://localhost:8000/dbmcp/docs
- **Web UI**: http://localhost:8000/dbmcp/ui
- **Health Check**: http://localhost:8000/dbmcp/health

#### MCP Server (Optional)
```bash
uv run mcp_run.py
```

The MCP server runs on port 4200 by default.

## Verification

### 1. Check API Health

```bash
curl http://localhost:8000/dbmcp/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

### 2. Test Authentication

```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
     http://localhost:8000/dbmcp/datasources
```

### 3. Access Web UI

Open http://localhost:8000/dbmcp/ui in your browser and enter your authentication token when prompted.

## Development Setup

### Installing Development Dependencies

```bash
uv sync --group dev
```

### Running Tests

```bash
uv run pytest
```

### Code Formatting

```bash
uv run black .
uv run isort .
```

### Type Checking

```bash
uv run mypy .
```

## Database Management

### Creating Migrations

When you modify the database schema:

```bash
uv run alembic revision --autogenerate -m "Description of changes"
```

### Applying Migrations

```bash
uv run alembic upgrade head
```

### Checking Migration Status

```bash
uv run alembic current
uv run alembic history
```

## Troubleshooting

### Common Issues

#### 1. Port Already in Use
If you get a "port already in use" error:

```bash
# Find the process using the port
lsof -i :8000

# Kill the process
kill -9 <PID>
```

#### 2. Database Connection Issues
- Ensure your database is running
- Check connection parameters in your datasource configuration
- Verify network connectivity

#### 3. Authentication Problems
- Regenerate your token: `uv run scripts/apptoken.py`
- Ensure you're using the correct token format: `Bearer <token>`
- Check that your JWT_SECRET_KEY is set correctly

#### 4. MCP Server Issues
- Ensure the MCP server is running on the correct port
- Check that your MCP client is configured correctly
- Verify authentication tokens are being passed correctly

### Getting Help

If you encounter issues:

1. Check the logs for error messages
2. Verify your environment configuration
3. Ensure all dependencies are installed correctly
4. Check the [API documentation](http://localhost:8000/dbmcp/docs) for endpoint details

## Next Steps

Now that you have DBMCP installed and running, you can:

1. **[Configure DataSources](./configure-datasources.md)** - Set up your database connections
2. **[Create Tools](./create-tools.md)** - Build MCP tools from your queries
3. **[Connect MCP Clients](./connect-mcp-clients.md)** - Integrate with AI assistants

Ready to configure your first datasource? Let's move on to the [DataSource Configuration Guide](./configure-datasources.md)!
