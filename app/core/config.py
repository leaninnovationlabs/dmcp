import os
from typing import List
from pydantic_settings import BaseSettings
from pydantic import ConfigDict, field_validator


class Settings(BaseSettings):
    """Application settings."""
    
    # Database
    database_url: str = "sqlite+aiosqlite:///./data/dmcp.db"
    
    # Security
    secret_key: str
    jwt_algorithm: str = "HS256"
    jwt_expiration_minutes: int = 600000
    
    debug: bool = True
    
    # Logging
    log_level: str = "INFO"
    
    # CORS
    allowed_origins: List[str] = ["http://localhost:3000", "http://localhost:8000"]
    
    # Database Connection Pool
    db_pool_size: int = 10
    db_max_overflow: int = 20
    
    # MCP Transport
    mcp_transport: str = "http"
    
    # MCP Server Configuration
    mcp_host: str = "0.0.0.0"
    mcp_port: int = 8000
    mcp_path: str = "/dmcp"
    mcp_log_level: str = "debug"


    # Default Admin Password
    default_admin_username: str = "admin"
    default_admin_password: str = "dochangethispassword"
    default_admin_password_encrypted: str = "Z0FBQUFBQm91R1RKVkdqRnlvMFlWcVdXVW9aS2tzRkxhaENybUV0eERJN09helF5X2ltdUNJN2tuTU4tQUg1Ukt1S3dlb3QxR2djOFNoeXRhMGdFNm01U2h2UVA0TkZrTWtHSDczdlpQek83ZS0xZW55czR2QXM9"
    
    @field_validator('secret_key')
    @classmethod
    def validate_secret_key(cls, v: str) -> str:
        """Validate that SECRET_KEY is properly set and not the default placeholder."""
        if not v or v.strip() == "":
            raise ValueError("SECRET_KEY must be set and cannot be empty")
        
        # Check for common placeholder values
        placeholder_values = [
            "your-secret-key-here-change-this-in-production",
            "change-this-in-production",
            "your-secret-key-here",
            "secret-key-placeholder",
            "default-secret-key"
        ]
        
        if v.strip() in placeholder_values:
            raise ValueError(
                "SECRET_KEY must be set to a secure value. "
                "Please set a proper SECRET_KEY in your environment variables or .env file. "
                "Do not use placeholder values."
            )
        
        # Ensure minimum length for security
        if len(v.strip()) < 32:
            raise ValueError(
                "SECRET_KEY must be at least 32 characters long for security. "
                f"Current length: {len(v.strip())}"
            )
        
        return v
    
    model_config = ConfigDict(env_file=".env", case_sensitive=False)


# Global settings instance
settings = Settings() 