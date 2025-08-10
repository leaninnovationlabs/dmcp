from fastmcp import FastMCP
from fastapi import FastAPI, Request
from starlette.middleware.cors import CORSMiddleware
from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Mount
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.mcp_server import MCPServer
from app.routes import auth, datasources, health, tools
from app.core.auth_middleware import BearerTokenMiddleware
from app.mcp.middleware.auth import AuthMiddleware
from app.mcp.middleware.logging import LoggingMiddleware

mcp = FastMCP("DBMCP")
server = MCPServer(mcp)


# Add middlewares
mcp.add_middleware(LoggingMiddleware())
mcp.add_middleware(AuthMiddleware())

# Build MCP ASGI app and mount it under FastAPI
mcp_app = mcp.http_app(path="/mcp")

starlette = Starlette(routes=[Mount("/dbmcp", app=mcp_app)], lifespan=mcp_app.lifespan)
mcp_app.mount("/ui", StaticFiles(directory="frontend", html=True), name="static")

app = FastAPI(
    title="DBMCP - Database Backend Server",
    description="A FastAPI server for managing database connections and executing queries",
    version="0.1.0",
    docs_url="/dbmcp/docs",
    redoc_url="/dbmcp/redoc",
    openapi_url="/dbmcp/openapi.json",
    lifespan=mcp_app.lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/dbmcp/api/test")
async def test(request: Request):
    return JSONResponse({"status": "healthy", "message": "DBMCP server is running"})

app.include_router(health.router, prefix="/dbmcp")
app.include_router(auth.router, prefix="/dbmcp")
app.include_router(datasources.router, prefix="/dbmcp")
app.include_router(tools.router, prefix="/dbmcp")

# Add Bearer token authentication middleware
app.add_middleware(BearerTokenMiddleware, ["/dbmcp/health", "/dbmcp/auth", "/dbmcp/docs", "/dbmcp/redoc", "/dbmcp/openapi.json", "/dbmcp/ui"])

app.mount("/", starlette)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.mcp_host, port=settings.mcp_port)
