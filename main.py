#!/usr/bin/env python3
"""
DBMCP Server - FastMCP Implementation

Enterprise-grade database MCP server using FastMCP 2.10 with custom routes.
"""

import asyncio
import json
import uvicorn

from fastmcp import FastMCP
from starlette.responses import JSONResponse

from app.core.config import settings
from app.database import init_db
from app.mcp_server import MCPServer
from app.services.auth_service import AuthService
from app.services.datasource_service import DatasourceService
from app.services.tool_service import ToolService
from app.database import get_db


mcp = FastMCP(name="DBMCP")
server = MCPServer(mcp)

def api_response(data=None, success=True, errors=None):
    """Universal API response envelope."""
    import json
    from datetime import datetime
    
    def json_serializer(obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        raise TypeError(f"Object of type {obj.__class__.__name__} is not JSON serializable")
    
    content = {
        "success": success,
        "data": data,
        "errors": errors or []
    }
    
    return JSONResponse(
        content=json.loads(json.dumps(content, default=json_serializer))
    )


@mcp.custom_route("/health", methods=["GET"])
async def health_check(request):
    """Health check endpoint."""
    return api_response({"status": "healthy", "message": "DBMCP server is running"})


@mcp.custom_route("/auth", methods=["POST"])
async def generate_token(request):
    """Generate JWT token endpoint."""
    try:
        body = await request.body()
        payload = json.loads(body) if body else {}
        
        auth_service = AuthService()
        token = auth_service.create_token(payload)
        
        return api_response({
            "token": token,
            "expires_in_minutes": auth_service.expiration_minutes
        })
    except Exception as e:
        return api_response(None, False, [f"Token generation failed: {str(e)}"])


@mcp.custom_route("/auth/validate", methods=["GET"])
async def validate_token(request):
    """Validate JWT token endpoint."""
    auth_header = request.headers.get("authorization", "")
    
    if not auth_header:
        return api_response(None, False, ["Authorization header is required"])
    
    auth_service = AuthService()
    try:
        payload = auth_service.validate_token(auth_header)
        return api_response({"payload": payload, "valid": True})
    except Exception as e:
        return api_response(None, False, [f"Authentication failed: {str(e)}"])


@mcp.custom_route("/datasources/field-config", methods=["GET"])
async def get_datasource_field_config(request):
    """Get field configuration for all datasource types."""
    field_configs = {
        "sqlite": {
            "database_type": "sqlite",
            "fields": [
                {
                    "name": "sqlite_database",
                    "type": "text",
                    "label": "Database File Path",
                    "required": True,
                    "placeholder": "/path/to/database.db",
                    "description": "Path to the SQLite database file"
                }
            ],
            "sections": [
                {
                    "id": "sqlite-config",
                    "title": "SQLite Configuration",
                    "description": "Configure your SQLite database connection"
                }
            ]
        },
        "postgresql": {
            "database_type": "postgresql",
            "fields": [
                {
                    "name": "host",
                    "type": "text",
                    "label": "Host",
                    "required": True,
                    "placeholder": "localhost"
                },
                {
                    "name": "port",
                    "type": "number",
                    "label": "Port",
                    "required": True,
                    "placeholder": "5432"
                },
                {
                    "name": "database",
                    "type": "text",
                    "label": "Database Name",
                    "required": True,
                    "placeholder": "mydatabase"
                },
                {
                    "name": "username",
                    "type": "text",
                    "label": "Username",
                    "required": True,
                    "placeholder": "myuser"
                },
                {
                    "name": "password",
                    "type": "password",
                    "label": "Password",
                    "required": True,
                    "placeholder": "mypassword"
                }
            ],
            "sections": [
                {
                    "id": "postgresql-config",
                    "title": "PostgreSQL Configuration",
                    "description": "Configure your PostgreSQL database connection"
                }
            ]
        }
    }
    return api_response(field_configs)


@mcp.custom_route("/datasources", methods=["POST"])
async def create_datasource(request):
    """Create a new datasource."""
    try:
        body = await request.body()
        data = json.loads(body) if body else {}
        
        # Transform frontend format to backend format
        transformed_data = {
            "name": data.get("name"),
            "database_type": data.get("database_type"),
            "database": data.get("database", "default"),  # Default database name
            "additional_params": data.get("connection_params", {})
        }
        
        # Extract specific fields from connection_params
        if "connection_params" in data:
            params = data["connection_params"]
            if "host" in params:
                transformed_data["host"] = params["host"]
            if "port" in params:
                transformed_data["port"] = params["port"]
            if "database" in params:
                transformed_data["database"] = params["database"]
            if "username" in params:
                transformed_data["username"] = params["username"]
            if "password" in params:
                transformed_data["password"] = params["password"]
            if "sqlite_database" in params:
                transformed_data["database"] = params["sqlite_database"]
        
        async for db in get_db():
            service = DatasourceService(db)
            from app.models.schemas import DatasourceCreate
            datasource_data = DatasourceCreate(**transformed_data)
            result = await service.create_datasource(datasource_data)
            return api_response(result.model_dump())
    except Exception as e:
        return api_response(None, False, [f"Failed to create datasource: {str(e)}"])


@mcp.custom_route("/datasources", methods=["GET"])
async def list_datasources(request):
    """List all datasources."""
    async for db in get_db():
        service = DatasourceService(db)
        result = await service.list_datasources()
        return api_response([ds.model_dump() for ds in result])


@mcp.custom_route("/datasources/{datasource_id}", methods=["GET"])
async def get_datasource(request):
    """Get specific datasource."""
    datasource_id = int(request.path_params.get("datasource_id"))
    
    async for db in get_db():
        service = DatasourceService(db)
        datasource = await service.get_datasource(datasource_id)
        if not datasource:
            return api_response(None, False, ["Datasource not found"])
        return api_response(datasource.model_dump())


@mcp.custom_route("/tools", methods=["GET"])
async def list_tools(request):
    """List all tools."""
    async for db in get_db():
        service = ToolService(db)
        result = await service.list_tools()
        return api_response([tool.model_dump() for tool in result])


@mcp.custom_route("/tools", methods=["POST"])
async def create_tool(request):
    """Create a new tool."""
    try:
        body = await request.body()
        data = json.loads(body) if body else {}
        
        async for db in get_db():
            service = ToolService(db)
            from app.models.schemas import ToolCreate
            tool_data = ToolCreate(**data)
            result = await service.create_tool(tool_data)
            return api_response(result.model_dump())
    except Exception as e:
        return api_response(None, False, [f"Failed to create tool: {str(e)}"])


@mcp.custom_route("/tools/{tool_id}", methods=["GET"])
async def get_tool(request):
    """Get specific tool."""
    tool_id = int(request.path_params.get("tool_id"))
    async for db in get_db():
        service = ToolService(db)
        tool = await service.get_tool(tool_id)
        if not tool:
            return api_response(None, False, ["Tool not found"])
        return api_response(tool.model_dump())


async def startup():
    """Initialize database on startup."""
    await init_db()


async def main():
    """Main entry point."""
    await startup()
    
    # Use FastMCP's native HTTP transport like jira server
    await mcp.run_async(
        transport="http",
        host=settings.mcp_host,
        port=settings.mcp_port,
        path="/mcp",
        stateless_http=True
    )


def main_sync():
    """Synchronous entry point."""
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Shutting down...")
    except Exception as e:
        print(f"Application error: {e}")
        raise

if __name__ == "__main__":
    main_sync()