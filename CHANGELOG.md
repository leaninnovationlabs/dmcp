# Changelog

All notable changes to this project will be documented in this file.

## [0.1.0] - 2025-08-24

### 🚀 Initial Release

DBMCP (Database Model Context Protocol) is a Python backend server built with FastAPI that enables you to connect to various databases and expose database operations as MCP tools for AI assistants.

#### ✨ Core Features

##### 🔐 Authentication & Security
- **JWT Token Authentication**: Secure bearer token-based authentication system
- **Token Generation & Validation**: Built-in token management with secure key handling
- **Encryption Support**: Cryptography-based security features
- **Middleware Protection**: Auth middleware for route protection

##### 🗄️ Database Connectivity
- **Multi-Database Support**: 
  - PostgreSQL (async operations with asyncpg)
  - MySQL/MariaDB (async operations with aiomysql)
  - SQLite (async operations with aiosqlite)
  - Databricks (cloud data warehouse integration)
- **Connection Management**: Robust connection pooling and error handling
- **Connection Testing**: Built-in connection validation and testing
- **Encrypted Credentials**: Secure storage of database credentials

##### 🛠️ Tool Management
- **Named Query Tools**: Store and manage parameterized queries as MCP tools
- **Jinja Template Support**: Advanced templating for dynamic query generation
- **Parameter Validation**: Automatic parameter type checking and validation
- **Tool Execution**: Execute queries with pagination and result formatting
- **Tool CRUD Operations**: Create, read, update, and delete tools via API

##### 🔌 MCP (Model Context Protocol) Integration
- **MCP Server**: Expose database operations as AI-accessible tools
- **Tool Discovery**: Automatic tool registration and discovery
- **HTTP Transport**: MCP server accessible via HTTP endpoints
- **AI Assistant Integration**: Seamless integration with Claude, ChatGPT, and other AI assistants

##### 🌐 Web Interface
- **Modern UI**: Clean, responsive web interface for management
- **Datasource Management**: Intuitive datasource configuration interface
- **Tool Management**: Visual tool creation and editing
- **Real-time Testing**: Connection testing and query validation
- **Navigation**: Sidebar-based navigation with authentication

##### 🏗️ Architecture & Infrastructure
- **FastAPI Backend**: High-performance async web framework
- **SQLAlchemy ORM**: Modern database abstraction layer
- **Alembic Migrations**: Database schema version control and management
- **Async/Await**: Full asynchronous support throughout the stack
- **Dependency Injection**: Clean service architecture with dependency management

##### 📊 Data Management
- **Query Execution**: Run SQL queries with parameter support
- **Result Pagination**: Built-in pagination for large result sets
- **Data Formatting**: Structured data output for AI consumption
- **Error Handling**: Comprehensive error handling and user feedback

##### 🔧 Development & Operations
- **Environment Configuration**: Flexible configuration via environment variables
- **Docker Support**: Containerized deployment with docker-compose
- **Testing Framework**: Comprehensive test suite with pytest
- **Code Quality**: Black, isort, flake8, and mypy integration
- **Documentation**: Extensive API documentation and user guides

##### 📚 API Endpoints
- **Health Check**: `/health` - System health monitoring
- **Authentication**: `/auth/*` - Token generation and validation
- **Datasources**: `/datasources/*` - Database connection management
- **Tools**: `/tools/*` - MCP tool management and execution
- **MCP Server**: `/dbmcp/mcp` - Model Context Protocol endpoints

#### 🎯 Use Cases
- **AI-Powered Data Analysis**: Enable AI assistants to query databases naturally
- **Database Administration**: Web-based database management interface
- **Data Exploration**: Create reusable query tools for data discovery
- **Integration Hub**: Connect multiple databases through a single interface
- **Development & Testing**: Local development environment for database operations

#### 🚀 Getting Started
1. Install dependencies with `uv sync`
2. Configure `SECRET_KEY` environment variable
3. Initialize database with `uv run alembic upgrade head`
4. Run server with `uv run main.py`
5. Access UI at `http://localhost:8000/dbmcp/ui`

#### 🔗 MCP Integration
- Launch MCP Inspector: `npx @modelcontextprotocol/inspector`
- Connect to: `http://127.0.0.1:8000/dbmcp`
- Use Authorization header: `Bearer <your-token>`

#### 📦 Dependencies
- **Core**: FastAPI, SQLAlchemy, Pydantic, Alembic
- **Database Drivers**: asyncpg, aiomysql, aiosqlite, databricks-sql-connector
- **Security**: PyJWT, cryptography
- **Templating**: Jinja2
- **MCP**: fastmcp
- **Development**: pytest, black, isort, flake8, mypy

---

*For detailed documentation, visit: https://dbmcp.opsloom.io/*

