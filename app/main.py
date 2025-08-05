from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
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
    allow_origins=settings.cors_allow_origins,
    allow_origin_regex=settings.cors_allow_origin_regex,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=settings.cors_allow_methods,
    allow_headers=settings.cors_allow_headers,
    expose_headers=settings.cors_expose_headers,
    max_age=settings.cors_max_age,
)

# Add Bearer token authentication middleware
app.add_middleware(
    BearerTokenMiddleware,
    excluded_paths=[
        "/dbmcp/health", 
        "/dbmcp/ui/", 
        "/dbmcp/ui", 
        "/dbmcp/docs", 
        "/dbmcp/redoc", 
        "/dbmcp/openapi.json",
        "/",  # Root redirect
        "/index.html",  # Index redirect
        "/dbmcp",  # DBMCP redirect
        "/dbmcp/",  # DBMCP slash redirect
        "/static/",  # Static assets
        "/frontend/"  # Frontend assets
    ]
)

# Include routers with /dbmcp prefix
app.include_router(health.router, prefix="/dbmcp")
app.include_router(datasources.router, prefix="/dbmcp")
app.include_router(tools.router, prefix="/dbmcp")
app.include_router(execute.router, prefix="/dbmcp")
# Backup functionality removed during PostgreSQL migration

# Add redirect routes for better UX
@app.get("/")
async def root_redirect():
    """Redirect root path to the UI."""
    return RedirectResponse(url="/dbmcp/ui/", status_code=301)

@app.get("/index.html")
async def index_redirect():
    """Serve index.html from frontend for root access."""
    return RedirectResponse(url="/dbmcp/ui/index.html", status_code=301)

@app.get("/dbmcp")
async def dbmcp_redirect():
    """Redirect /dbmcp to the UI."""
    return RedirectResponse(url="/dbmcp/ui/", status_code=301)

@app.get("/dbmcp/")
async def dbmcp_slash_redirect():
    """Redirect /dbmcp/ to the UI."""
    return RedirectResponse(url="/dbmcp/ui/", status_code=301)

@app.get("/dbmcp/ui")
async def ui_redirect():
    """Redirect /dbmcp/ui to /dbmcp/ui/ with trailing slash."""
    return RedirectResponse(url="/dbmcp/ui/", status_code=301)

# Mount static files
app.mount("/dbmcp/ui", StaticFiles(directory="frontend", html=True), name="ui-static")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)