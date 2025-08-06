---
# https://vitepress.dev/reference/default-theme-home-page
layout: home

hero:
  name: "DBMCP Server"
  text: "Database Backend Server with MCP Support"
  tagline: Connect AI assistants to your databases through natural language
  actions:
    - theme: brand
      text: Introduction
      link: /introduction
    - theme: alt
      text: Get Started
      link: /get-started

features:
  - title: Multi-Database Support
    details: Connect to PostgreSQL, MySQL, SQLite, and Databricks with unified interface
    icon: 🗄️
  - title: MCP Integration
    details: Expose database operations as tools for AI assistants using the Model Context Protocol
    icon: 🤖
  - title: Jinja Templating
    details: Dynamic SQL queries with parameter support and conditional logic
    icon: 📝
  - title: Web Interface
    details: Intuitive UI for managing datasources, tools, and testing connections
    icon: 🌐
  - title: Security First
    details: JWT authentication, encrypted credentials, and SSL support
    icon: 🔐
  - title: Easy Setup
    details: Simple installation with uv package manager and comprehensive documentation
    icon: ⚡

---

## Quick Start

Get up and running with DBMCP in minutes:

```bash
# Install dependencies
uv sync

# Initialize database
uv run alembic upgrade head

# Generate authentication token
uv run scripts/apptoken.py

# Start the API server
uv run api_run.py

# Start the MCP server (optional)
uv run mcp_run.py
```

## Documentation

- **[Introduction](./introduction.md)** - Learn about DBMCP and its features
- **[Installation & Setup](./get-started.md)** - Get DBMCP running on your system
- **[Configure DataSources](./configure-datasources.md)** - Set up database connections
- **[Create Tools](./create-tools.md)** - Build MCP tools from your queries
- **[Connect MCP Clients](./connect-mcp-clients.md)** - Integrate with AI assistants

## API Documentation

- **Swagger UI**: http://localhost:8000/dbmcp/docs
- **Web Interface**: http://localhost:8000/dbmcp/ui
- **Health Check**: http://localhost:8000/dbmcp/health

## Supported Databases

- **PostgreSQL** - Full async support with SSL
- **MySQL/MariaDB** - Complete MySQL support
- **SQLite** - Lightweight local database
- **Databricks** - Cloud data warehouse integration

## MCP Clients

- **Claude Desktop** - Local AI assistant integration
- **MCP Inspector** - Web-based testing tool
- **Custom Clients** - Build your own MCP clients

