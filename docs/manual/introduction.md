---
outline: deep
---

# Introduction

DBMCP (Database Model Context Protocol) is a Python backend server built with FastAPI that enables you to connect to various databases and expose database operations as MCP (Model Context Protocol) tools for AI assistants. This allows AI models to interact with your databases through natural language, making data access and analysis more intuitive and accessible.

## What is DBMCP?

DBMCP serves as a bridge between AI assistants and your databases. It provides:

- **Database Connectivity**: Connect to multiple database types (PostgreSQL, MySQL, SQLite, Databricks)
- **Query Management**: Store and manage parameterized queries with Jinja template support
- **MCP Integration**: Expose database operations as tools that AI assistants can use
- **Web UI**: Simple interface for managing datasources and tools


## Architecture Overview

```
┌─────────────────┐    ┌──────────────┐    ┌─────────────────┐
│   AI Assistant  │    │   DBMCP      │    │   Databases     │
│   (Claude, etc) │◄──►│   Server     │◄──►│   (PostgreSQL,  │
│                 │    │              │    │    MySQL, etc)  │
└─────────────────┘    └──────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌──────────────┐
                       │   Web UI     │
                       │   (Optional) │
                       └──────────────┘
```

## Key Features

### <i class="fas fa-database"></i> Multi-Database Support
Currently supports the following database systems:
- **PostgreSQL** - Full support with async operations
- **MySQL** - Complete MySQL/MariaDB support
- **SQLite** - Lightweight local database support
- **Databricks** - Cloud data warehouse integration
- **Coming Soon** - Snowflake, Redshift, and more


### <i class="fas fa-robot"></i> MCP Tool Integration
Transform your database queries into AI-accessible tools:
- Create named queries with parameters
- Expose complex SQL operations as simple tools
- Support for Jinja templating in queries
- Automatic parameter validation and type checking

### <i class="fas fa-globe"></i> Web Interface
- Intuitive UI for managing datasources
- Tool creation and management interface
- Real-time query testing and validation
- Connection testing and monitoring


## Getting Started

The typical workflow involves:

1. **<i class="fas fa-download"></i> Installation** - Set up the DBMCP server
2. **<i class="fas fa-cog"></i> Configuration** - Configure your database connections
3. **<i class="fas fa-tools"></i> Tool Creation** - Create MCP tools from your queries
4. **<i class="fas fa-plug"></i> MCP Integration** - Connect AI assistants to your tools

Ready to get started? Check out the [Installation Guide](./get-started.md) to begin your DBMCP journey!
