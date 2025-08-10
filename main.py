#!/usr/bin/env python3
"""
DBMCP Server - FastMCP Implementation

Enterprise-grade database MCP server using FastMCP 2.10 with custom routes.
"""
import asyncio
import json
import uvicorn

from fastmcp import FastMCP
from starlette.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from starlette.routing import Mount
from starlette.applications import Starlette
from app.core.config import settings
from app.database import init_db
from app.mcp.middleware.auth import AuthMiddleware
from app.mcp_server import MCPServer
from app.routes.auth import AuthRouter
from app.routes.health import HealthRouter
from app.routes.datasources import DatasourcesRouter
from app.routes.tools import ToolsRouter
import json

mcp = FastMCP(name="DBMCP")
server = MCPServer(mcp)


mcp_app = mcp.http_app(path="/mcp")

# Mount MCP functionality
starlette_app = Starlette(routes=[ Mount("/", app=mcp_app) ], lifespan=mcp_app.lifespan)

app = FastAPI(lifespan=mcp_app.lifespan)

# Configure CORS settings
origins = ["http://localhost:3000", "http://localhost:8000", "http://localhost:4200", "http://127.0.0.1:5500"]  # Adjust for your frontend origin

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


auth_middleware = AuthMiddleware()
cors_middleware = CORSMiddleware(
    app=mcp,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"]
)


# TODO: Middleware is not working as expected, need to fix it
mcp.add_middleware(auth_middleware)
mcp.add_middleware(cors_middleware)

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
    
    # Start FastMCP HTTP server with CORS middleware
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