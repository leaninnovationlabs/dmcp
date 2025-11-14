from fastapi import FastAPI, Request
from fastapi.responses import FileResponse
from fastmcp import FastMCP
from fastmcp.exceptions import NotFoundError
from starlette.applications import Starlette
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse, RedirectResponse
from starlette.routing import Mount

from app.core.auth_middleware import BearerTokenMiddleware
from app.core.config import settings
from app.mcp.middleware.auth import AuthMiddleware
from app.mcp.middleware.logging import LoggingMiddleware
from app.mcp.middleware.tools import CustomizeToolsList
from app.mcp_server import MCPServer
from app.routes import auth, datasources, health, tags, tools, users
from app.services.server_provider import set_server

mcp = FastMCP("DMCP")
server = MCPServer(mcp)
set_server(server)


# Add middlewares
mcp.add_middleware(LoggingMiddleware())
mcp.add_middleware(AuthMiddleware())
mcp.add_middleware(CustomizeToolsList())

# Build MCP ASGI app and mount it under FastAPI (stateless for compatibility with tidd)
mcp_app = mcp.http_app(path="/mcp/", stateless_http=True)

starlette = Starlette(routes=[Mount(settings.mcp_path, app=mcp_app)], lifespan=mcp_app.lifespan)
# mcp_app.mount("/ui", StaticFiles(directory="public", html=True), name="static")

app = FastAPI(
    title="DMCP - Database Backend Server",
    description="A FastAPI server for managing database connections and executing queries",
    version="0.1.0",
    docs_url=f"{settings.mcp_path}/docs",
    redoc_url=f"{settings.mcp_path}/redoc",
    openapi_url=f"{settings.mcp_path}/openapi.json",
    lifespan=mcp_app.lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/dmcp/tools/refresh")
async def refresh_tools(request: Request):
    """Refresh tool registry by syncing with database."""
    try:
        # Get currently registered tools
        registered_tools = await mcp.get_tools()
        
        # Unregister all database tools
        removed_count = 0
        for tool_name in registered_tools.keys():
            try:
                mcp.remove_tool(tool_name)
                removed_count += 1
            except NotFoundError:
                # Tool was not found in the registry; safe to ignore as it may have already been removed.
                pass
        
        # Re-register all tools from database
        server._register_database_tools()
        
        # Get count of registered tools after refresh
        db_tools = server._list_tools()
        registered_count = len(db_tools)
        
        return JSONResponse({
            "status": "success",
            "message": "Tools refreshed successfully",
            "removed": removed_count,
            "registered": registered_count
        })
    except Exception as e:
        return JSONResponse({
            "status": "error",
            "message": str(e)
        }, status_code=500)


app.include_router(health.router, prefix=f"{settings.mcp_path}")
app.include_router(auth.router, prefix=f"{settings.mcp_path}")
app.include_router(datasources.router, prefix=f"{settings.mcp_path}")
app.include_router(tags.router, prefix=f"{settings.mcp_path}")
app.include_router(tools.router, prefix=f"{settings.mcp_path}")
app.include_router(users.router, prefix=f"{settings.mcp_path}")


# Serve static assets for React app
@app.get("/dmcp/ui/assets/{file_path:path}")
async def serve_react_assets(file_path: str):
    return FileResponse(f"public/assets/{file_path}")


# Serve logo assets
@app.get("/dmcp/ui/logo.webp")
async def serve_logo_webp():
    return FileResponse("public/logo.webp")


@app.get("/dmcp/ui/logo.png")
async def serve_logo_png():
    return FileResponse("public/logo.png")


@app.get("/dmcp/ui/logo.svg")
async def serve_vite_svg():
    return FileResponse("public/logo.svg")


# Catch-all route for React app - serves index.html for any /ui/ path
@app.get("/dmcp/ui/{path:path}")
async def serve_react_app(path: str):
    return FileResponse("public/index.html")


# Add a redirect to the root path to /dmcp/ui
@app.get("/")
async def redirect_to_ui():
    return RedirectResponse("dmcp/ui/")


@app.get("/dmcp")
async def redirect_to_dmcp_ui():
    return RedirectResponse("dmcp/ui/")


# Add Bearer token authentication middleware
app.add_middleware(
    BearerTokenMiddleware,
    [
        f"{settings.mcp_path}/health",
        f"{settings.mcp_path}/auth",
        f"{settings.mcp_path}/docs",
        f"{settings.mcp_path}/redoc",
        f"{settings.mcp_path}/openapi.json",
        f"{settings.mcp_path}/ui",
    ],
)

app.mount("/", starlette)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host=settings.mcp_host, port=settings.mcp_port)
