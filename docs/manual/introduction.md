---
outline: deep
---

# Introduction

DBMCP (Database Model Context Protocol) is a powerful Python backend server built with FastAPI that enables you to connect to various databases and expose database operations as MCP (Model Context Protocol) tools for AI assistants. This allows AI models to interact with your databases through natural language, making data access and analysis more intuitive and accessible.

## What is DBMCP?

DBMCP serves as a bridge between AI assistants and your databases. It provides:

- **Database Connectivity**: Connect to multiple database types (PostgreSQL, MySQL, SQLite, Databricks)
- **Query Management**: Store and manage parameterized queries with Jinja template support
- **MCP Integration**: Expose database operations as tools that AI assistants can use
- **Authentication**: Secure access with JWT token authentication
- **Web UI**: Simple interface for managing datasources and tools

## Key Features

### 🗄️ Multi-Database Support
Connect to various database systems:
- **PostgreSQL** - Full support with async operations
- **MySQL** - Complete MySQL/MariaDB support
- **SQLite** - Lightweight local database support
- **Databricks** - Cloud data warehouse integration

### 🔧 MCP Tool Integration
Transform your database queries into AI-accessible tools:
- Create named queries with parameters
- Expose complex SQL operations as simple tools
- Support for Jinja templating in queries
- Automatic parameter validation and type checking

### 🔐 Security & Authentication
- JWT-based authentication system
- Encrypted database credentials storage
- Role-based access control (coming soon)
- Secure connection handling

### 🌐 Web Interface
- Intuitive UI for managing datasources
- Tool creation and management interface
- Real-time query testing and validation
- Connection testing and monitoring

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

## Use Cases

### 1. Business Intelligence
- Create tools for common business queries
- Allow AI to generate reports and insights
- Automate data analysis workflows

### 2. Data Exploration
- Enable AI to explore database schemas
- Create tools for ad-hoc queries
- Support data discovery and validation

### 3. Application Development
- Expose database operations as API endpoints
- Create tools for common CRUD operations
- Enable AI-assisted application development

### 4. Data Migration & ETL
- Create tools for data transformation
- Enable AI-assisted data pipeline creation
- Support complex data operations

## Getting Started

The typical workflow involves:

1. **Installation** - Set up the DBMCP server
2. **Configuration** - Configure your database connections
3. **Tool Creation** - Create MCP tools from your queries
4. **MCP Integration** - Connect AI assistants to your tools
5. **Usage** - Start using AI-powered database operations

Ready to get started? Check out the [Installation Guide](./get-started.md) to begin your DBMCP journey!
