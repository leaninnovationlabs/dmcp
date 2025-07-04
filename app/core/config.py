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
    
    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = True
    
    # Logging
    log_level: str = "INFO"
    
    # CORS
    allowed_origins: List[str] = ["http://localhost:3000", "http://localhost:8000"]
    
    # Database Connection Pool
    db_pool_size: int = 10
    db_max_overflow: int = 20
    
    # Transport
    transport: str = "stdio"
    
    model_config = ConfigDict(env_file=".env", case_sensitive=False)


# Global settings instance
settings = Settings() 