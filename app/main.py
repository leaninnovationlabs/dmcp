from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import uvicorn

from .database import init_db
from .routes import datasources, tools, execute, health
from .core.config import settings
from .core.auth_middleware import BearerTokenMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await init_db()
    yield
    # Shutdown
    pass

app = FastAPI(
    title="DBMCP - Database Backend Server",
    description="A FastAPI server for managing database connections and executing queries",
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/dbmcp/docs",
    redoc_url="/dbmcp/redoc",
    openapi_url="/dbmcp/openapi.json"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add Bearer token authentication middleware
app.add_middleware(BearerTokenMiddleware, ["/dbmcp/health", "/dbmcpui/*", "/dbmcp/docs", "/dbmcp/redoc", "/dbmcp/openapi.json", "/dbmcp/ui"])

# Include routers with /dbmcp prefix
app.include_router(health.router, prefix="/dbmcp")
app.include_router(datasources.router, prefix="/dbmcp")
app.include_router(tools.router, prefix="/dbmcp")
app.include_router(execute.router, prefix="/dbmcp")

# Mount static files
app.mount("/dbmcp/ui", StaticFiles(directory="frontend", html=True), name="static")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)