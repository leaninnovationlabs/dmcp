import os
import json
import boto3
import logging
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import ConfigDict, Field


def get_database_url_from_parameter_store(parameter_name: str, region: str = "us-east-1") -> str:
    """Fetch database URL from AWS Parameter Store and Secrets Manager."""
    try:
        ssm = boto3.client('ssm', region_name=region)
        secrets = boto3.client('secretsmanager', region_name=region)
        
        # Get database connection details from Parameter Store
        host_response = ssm.get_parameter(Name=f"/{parameter_name.split('/')[1]}/dbmcp/database_host", WithDecryption=True)
        port_response = ssm.get_parameter(Name=f"/{parameter_name.split('/')[1]}/dbmcp/database_port")
        dbname_response = ssm.get_parameter(Name=f"/{parameter_name.split('/')[1]}/dbmcp/database_name")
        username_response = ssm.get_parameter(Name=f"/{parameter_name.split('/')[1]}/dbmcp/database_username", WithDecryption=True)
        secret_arn_response = ssm.get_parameter(Name=f"/{parameter_name.split('/')[1]}/dbmcp/database_secret_arn", WithDecryption=True)
        
        # Get password from Secrets Manager
        secret_response = secrets.get_secret_value(SecretId=secret_arn_response['Parameter']['Value'])
        secret_data = json.loads(secret_response['SecretString'])
        
        # Construct database URL
        host = host_response['Parameter']['Value']
        port = port_response['Parameter']['Value']
        dbname = dbname_response['Parameter']['Value']
        username = username_response['Parameter']['Value']
        password = secret_data['password']
        
        database_url = f"postgresql+asyncpg://{username}:{password}@{host}:{port}/{dbname}"
        return database_url
        
    except Exception as e:
        logging.error(f"Failed to fetch database URL from Parameter Store/Secrets Manager: {e}")
        raise


class Settings(BaseSettings):
    """Application settings."""
    
    # Parameter Store configuration
    use_parameter_store: bool = Field(default=False, env="USE_PARAMETER_STORE")
    database_url_parameter: Optional[str] = Field(default=None, env="DATABASE_URL_PARAMETER")
    aws_region: str = Field(default="us-east-1", env="AWS_DEFAULT_REGION")
    
    # Database
    database_url: str = Field(default="postgresql+asyncpg://dbmcp:dbmcp@localhost/dbmcp", env="DATABASE_URL")
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # If using Parameter Store, fetch the database URL
        if self.use_parameter_store and self.database_url_parameter:
            try:
                self.database_url = get_database_url_from_parameter_store(
                    self.database_url_parameter, 
                    self.aws_region
                )
                logging.info("Successfully fetched database URL from Parameter Store")
            except Exception as e:
                logging.error(f"Failed to fetch database URL from Parameter Store: {e}")
                # Fall back to environment variable if Parameter Store fails
                if "DATABASE_URL" in os.environ:
                    self.database_url = os.environ["DATABASE_URL"]
                    logging.info("Using DATABASE_URL environment variable as fallback")
                else:
                    logging.warning("Using default database URL as fallback")
    
    # Security
    secret_key: str = "your-secret-key-here-change-this-in-production"
    
    # JWT Settings
    jwt_secret_key: str = "Pukkjb4TA9azqwMBt9oLsR0qRFHp-YSJgBQcvSEgvJ0"
    jwt_algorithm: str = "HS256"
    jwt_expiration_minutes: int = 60
    
    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = True
    
    # Logging
    log_level: str = "INFO"
    
    # CORS Configuration
    # List of origins that should be permitted to make cross-origin requests
    # Examples: ["https://example.com", "https://subdomain.example.com"]
    # Use ["*"] to allow any origin (not recommended for production with credentials)
    cors_allow_origins: List[str] = [
        "http://localhost:3000", 
        "http://localhost:8000", 
        "http://localhost:8002", 
        "http://localhost:8080",
        "https://dbmcp.opsloom.io",
        "https://dbmcp-staging.opsloom.io",
        "https://dbmcp-production.opsloom.io"
    ]
    
    # Regex string to match against origins (alternative to allow_origins)
    # Example: "https://.*\.example\.com" to allow all subdomains of example.com
    cors_allow_origin_regex: Optional[str] = r"https://.*\.opsloom\.io"
    
    # HTTP methods that should be allowed for cross-origin requests
    # Use ["*"] to allow all standard methods, or specify: ["GET", "POST", "PUT", "DELETE"]
    cors_allow_methods: List[str] = ["*"]
    
    # HTTP request headers that should be supported for cross-origin requests
    # Use ["*"] to allow all headers, or specify: ["Authorization", "Content-Type"]
    cors_allow_headers: List[str] = ["*"]
    
    # Whether cookies should be supported for cross-origin requests
    # Set to False if you don't need cookies/auth headers in cross-origin requests
    cors_allow_credentials: bool = True
    
    # Response headers that should be made accessible to the browser
    # Example: ["X-Custom-Header", "X-Another-Header"]
    cors_expose_headers: List[str] = []
    
    # Maximum time in seconds for browsers to cache CORS responses
    cors_max_age: int = 600
    
    # Database Connection Pool
    db_pool_size: int = 10
    db_max_overflow: int = 20
    
    # Transport  
    transport: str = "stdio"
    
    # S3 Configuration for state backup
    s3_bucket_name: str = "opsloom-state-bucket"
    aws_access_key_id: Optional[str] = None
    aws_secret_access_key: Optional[str] = None
    
    model_config = ConfigDict(env_file=".env", case_sensitive=False)


# Global settings instance
settings = Settings() 