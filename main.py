from fastmcp import FastMCP
from fastapi import FastAPI, Request
from starlette.middleware.cors import CORSMiddleware
from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Mount
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.mcp_server import MCPServer
from app.routes.health import HealthRouter
from app.routes.auth import AuthRouter
from app.routes.datasources import DatasourcesRouter
from app.routes.tools import ToolsRouter

mcp = FastMCP("DBMCP")
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
    

app.mount("/", starlette)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.mcp_host, port=settings.mcp_port)
