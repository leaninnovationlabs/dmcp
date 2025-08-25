---
outline: deep
---

# Installation & Setup

This guide will walk you through installing and setting up DMCP on your system.

## Prerequisites

Before installing DMCP, ensure you have:

- **Python 3.10 or higher**
- **uv package manager** (recommended) or pip
- **Git** (for cloning the repository)

### <i class="fas fa-download"></i> Installing uv (Recommended)

uv is a fast Python package installer and resolver, written in Rust. It's the recommended way to manage dependencies for this project.

```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Or using pip
pip install uv
```

## Installation Steps

### <i class="fas fa-clone"></i> 1. Clone the Repository

```bash
git clone <repository-url>
cd dmcp
```

### <i class="fas fa-box"></i> 2. Install Dependencies

Using uv (recommended):
```bash
uv sync
```

Or using pip:
```bash
pip install -r requirements.txt
```

### <i class="fas fa-cog"></i> 3. Environment Configuration

Create a `.env` file in the project root:

```bash
cp env.example .env
```

Edit the `.env` file with your configuration:

```bash
# Database Configuration
DATABASE_URL=sqlite+aiosqlite:///./dmcp.db

# Security
SECRET_KEY=your-secret-key-here-change-this-in-production

# JWT Configuration
JWT_SECRET_KEY=jwt-secret-key-change-this-in-production
JWT_ALGORITHM=HS256
JWT_EXPIRATION_MINUTES=60


# Server Configuration
HOST=0.0.0.0
PORT=8000
DEBUG=true

# Logging
LOG_LEVEL=INFO

# CORS, add your frontend url here if its served from a different port and domain
ALLOWED_ORIGINS=["http://localhost:3000", "http://localhost:8000"]

# MCP Server Configuration
MCP_TRANSPORT=stdio
MCP_HOST=127.0.0.1
MCP_PORT=8000
MCP_PATH=/dmcp
MCP_LOG_LEVEL=debug
```

### <i class="fas fa-database"></i> 4. Initialize the Database

```bash
uv run alembic upgrade head
```

### <i class="fas fa-key"></i> 5. Generate Authentication Token

Create a token for API access:

```bash
uv run scripts/apptoken.py
```

This will output a token that you'll use for authentication.

### <i class="fas fa-server"></i> 6. Start the Server


#### API Server
```bash
uv run main.py
```

The API server will be available at:
- **API Documentation**: http://localhost:8000/dmcp/docs (when server is running)
- **Web UI**: http://localhost:8000/dmcp/ui (when server is running)
- **Health Check**: http://localhost:8000/dmcp/health (when server is running)


The MCP server runs on port 8000 by default.

## Verification

### <i class="fas fa-heartbeat"></i> 1. Check API Health

```bash
curl http://localhost:8000/dmcp/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

### <i class="fas fa-lock"></i> 2. Test Authentication

```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
     http://localhost:8000/dmcp/datasources
```

### <i class="fas fa-desktop"></i> 3. Access Web UI

Open http://localhost:8000/dmcp/ui in your browser and enter your authentication token when prompted.

## Development Setup

### <i class="fas fa-code"></i> Installing Development Dependencies

```bash
uv sync --group dev
```

### <i class="fas fa-vial"></i> Running Tests

```bash
uv run pytest
```



## Troubleshooting

### Common Issues

#### <i class="fas fa-exclamation-triangle"></i> 1. Port Already in Use
If you get a "port already in use" error:

```bash
# Find the process using the port
lsof -i :8000

# Kill the process
kill -9 <PID>
```

#### <i class="fas fa-database"></i> 2. Database Connection Issues
- Ensure your database is running
- Check connection parameters in your datasource configuration
- Verify network connectivity

#### <i class="fas fa-key"></i> 3. Authentication Problems
- Regenerate your token: `uv run scripts/apptoken.py`
- Ensure you're using the correct token format: `Bearer <token>`
- Check that your JWT_SECRET_KEY is set correctly

#### <i class="fas fa-plug"></i> 4. MCP Server Issues
- Ensure the MCP server is running on the correct port
- Check that your MCP client is configured correctly
- Verify authentication tokens are being passed correctly

## Next Steps

Now that you have DMCP installed and running, you can:

1. **[Configure DataSources](./configure-datasources.md)** - Set up your database connections
2. **[Create Tools](./create-tools.md)** - Build MCP tools from your queries
3. **[Connect MCP Clients](./connect-mcp-clients.md)** - Integrate with AI assistants

Ready to configure your first datasource? Let's move on to the [DataSource Configuration Guide](./configure-datasources.md)!
