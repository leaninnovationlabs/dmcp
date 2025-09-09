from fastmcp import FastMCP
from fastapi import FastAPI, Request
from starlette.middleware.cors import CORSMiddleware
from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Mount
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.mcp.middleware.tools import CustomizeToolsList
from app.mcp_server import MCPServer
from app.routes import auth, datasources, health, tools, users
from app.core.auth_middleware import BearerTokenMiddleware
from app.mcp.middleware.auth import AuthMiddleware
from app.mcp.middleware.logging import LoggingMiddleware

mcp = FastMCP("DMCP")
server = MCPServer(mcp)


# Add middlewares
mcp.add_middleware(LoggingMiddleware())
mcp.add_middleware(AuthMiddleware())
mcp.add_middleware(CustomizeToolsList())

# Build MCP ASGI app and mount it under FastAPI (stateless for compatibility with tidd)
mcp_app = mcp.http_app(path="/mcp", stateless_http=True)

starlette = Starlette(routes=[Mount(settings.mcp_path, app=mcp_app)], lifespan=mcp_app.lifespan)
mcp_app.mount("/ui", StaticFiles(directory="public", html=True), name="static")

app = FastAPI(
    title="DMCP - Database Backend Server",
    description="A FastAPI server for managing database connections and executing queries",
    version="0.1.0",
    docs_url=f"{settings.mcp_path}/docs",
    redoc_url=f"{settings.mcp_path}/redoc",
    openapi_url=f"{settings.mcp_path}/openapi.json",
    lifespan=mcp_app.lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/dmcp/tools/refresh")
async def test(request: Request):
    server._register_database_tools()
    return JSONResponse({"status": "healthy", "message": "DMCP server is running"})

app.include_router(health.router, prefix=f"{settings.mcp_path}")
app.include_router(auth.router, prefix=f"{settings.mcp_path}")
app.include_router(datasources.router, prefix=f"{settings.mcp_path}")
app.include_router(tools.router, prefix=f"{settings.mcp_path}")
app.include_router(users.router, prefix=f"{settings.mcp_path}")

# Add Bearer token authentication middleware
app.add_middleware(BearerTokenMiddleware, [f"{settings.mcp_path}/health", 
    f"{settings.mcp_path}/auth", 
    f"{settings.mcp_path}/docs", 
    f"{settings.mcp_path}/redoc", 
    f"{settings.mcp_path}/openapi.json", 
    f"{settings.mcp_path}/ui"])

app.mount("/", starlette)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.mcp_host, port=settings.mcp_port)