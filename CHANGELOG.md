# Changelog

All notable changes to this project will be documented in this file.

## [0.1.0] - 2025-08-24

### 🚀 Initial Release

Data MCP (Data Model Context Protocol) is a Python backend server built with FastAPI that enables you to connect to any data source via query, API, or code and expose data operations as MCP tools for AI assistants.

#### ✨ Core Features

##### 🗄️ Data Source Connectivity
- **Multi-Data Source Support**: 
  - PostgreSQL (async operations with asyncpg)
  - MySQL/MariaDB (async operations with aiomysql)
  - SQLite (async operations with aiosqlite)
  - Databricks (cloud data warehouse integration)
  - APIs (HTTP request capabilities for external services)
- **Connection Management**: Robust connection pooling and error handling
- **Connection Testing**: Built-in connection validation and testing

##### 🛠️ Tool Management
- **Named Operation Tools**: Store and manage parameterized operations as MCP tools
- **Jinja Template Support**: Advanced templating for dynamic operation generation
- **Parameter Validation**: Automatic parameter type checking and validation
- **Tool Execution**: Execute operations with pagination and result formatting
- **Tool CRUD Operations**: Create, read, update, and delete tools via API

##### 🔌 MCP (Model Context Protocol) Integration
- **MCP Server**: Expose data operations as AI-accessible tools
- **Tool Discovery**: Automatic tool registration and discovery
- **HTTP Transport**: MCP server accessible via HTTP endpoints
- **AI Assistant Integration**: Seamless integration with Claude, ChatGPT, and other AI assistants

##### 🌐 Web Interface
- **UI**: Clean, simple interface for tools management
- **Datasource Management**: Intuitive datasource configuration interface
- **Tool Management**: Visual tool creation and editing

##### 🏗️ Architecture & Infrastructure
- **FastAPI Backend**: High-performance async web framework
- **SQLAlchemy ORM**: Modern database abstraction layer
- **Alembic Migrations**: Database schema version control and management
- **Dependency Injection**: Clean service architecture with dependency management

#### 🎯 Use Cases
- **AI-Powered Data Analysis**: Enable AI assistants to query data sources naturally
- **Data Source Administration**: Web-based data source management interface
- **Data Exploration**: Create reusable operation tools for data discovery
- **Integration Hub**: Connect multiple data sources through a single interface
- **Development & Testing**: Local development environment for data operations

---

*For detailed documentation, visit: https://dmcp.opsloom.io/*

