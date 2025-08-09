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
from app.core.exceptions import AuthenticationError
from app.core.token_processor import get_payload
from app.database import init_db
from app.mcp_server import MCPServer
from app.routes.auth import AuthRouter
from app.routes.health import HealthRouter
from app.core.responses import api_response
from app.services.auth_service import AuthService
from app.services.datasource_service import DatasourceService
from app.services.tool_service import ToolService
from app.database import get_db
from app.routes.datasources import DatasourcesRouter
from app.routes.tools import ToolsRouter
import json
from datetime import datetime


mcp = FastMCP(name="DBMCP")
server = MCPServer(mcp)


# Register routes
health_router = HealthRouter(mcp)
health_router.register_routes()

auth_router = AuthRouter(mcp)
auth_router.register_routes()

datasources_router = DatasourcesRouter(mcp)
datasources_router.register_routes()

tools_router = ToolsRouter(mcp)
tools_router.register_routes()



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