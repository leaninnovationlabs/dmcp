import os
from typing import List
from pydantic_settings import BaseSettings
from pydantic import ConfigDict


class Settings(BaseSettings):
    """Application settings."""
    
    # Database
    database_url: str = "sqlite+aiosqlite:///./dbmcp.db"
    
    # Security
    secret_key: str = "your-secret-key-here-change-this-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expiration_minutes: int = 600000
    
    debug: bool = True
    
    # Logging
    log_level: str = "INFO"
    
    # CORS
    allowed_origins: List[str] = []
    
    # Database Connection Pool
    db_pool_size: int = 10
    db_max_overflow: int = 20
    
    # MCP Transport
    mcp_transport: str = "http"
    
    # MCP Server Configuration
    mcp_host: str = "0.0.0.0"
    mcp_port: int = 8000
    mcp_path: str = "/dbmcp"
    mcp_log_level: str = "debug"
    
    model_config = ConfigDict(env_file=".env", case_sensitive=False)


# Global settings instance
settings = Settings() 