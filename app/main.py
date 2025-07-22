from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import uvicorn

from .database import init_db
from .routes import datasources, tools, execute, health
from .core.config import settings


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
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include routers with /dbmcp prefix
app.include_router(health.router, prefix="/dbmcp")
app.include_router(datasources.router, prefix="/dbmcp")
app.include_router(tools.router, prefix="/dbmcp")
app.include_router(execute.router, prefix="/dbmcp")

# Mount static files
app.mount("/dbmcpui", StaticFiles(directory="frontend", html=True), name="static")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 