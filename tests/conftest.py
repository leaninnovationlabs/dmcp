#!/usr/bin/env python3
"""
Pytest configuration and fixtures for DBMCP tests.
Simplified for real HTTP testing against http://localhost:8000
"""

import os
import pytest
import httpx
from typing import Dict, Any

# Add the app directory to Python path
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.models.schemas import DatabaseType
from app.core.jwt_validator import jwt_validator


@pytest.fixture(scope="session")
def api_base_url():
    """Get the API base URL."""
    return "http://localhost:8000"


@pytest.fixture
def http_client():
    """Create an HTTP client for API requests."""
    return httpx.Client(timeout=30.0)


@pytest.fixture
def auth_headers():
    """Create authentication headers for API requests."""
    payload = {
        "user_id": 123,
        "username": "test_user",
        "email": "test@example.com"
    }
    print(f"+++++ Creating token for user: {payload}")
    token = jwt_validator.create_token(payload)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def postgres_config():
    """Get PostgreSQL configuration from test environment."""
    # Load test environment variables
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(__file__), '.test.env'))
    
    return {
        "name": "Test PostgreSQL Database",
        "database_type": DatabaseType.POSTGRESQL.value,
        "host": os.getenv("TEST_DB_HOST", "localhost"),
        "port": int(os.getenv("TEST_DB_PORT", "5432")),
        "database": os.getenv("TEST_DB_NAME", "test_db"),
        "username": os.getenv("TEST_DB_USER", "postgres"),
        "password": os.getenv("TEST_DB_PASSWORD", "password"),
        "ssl_mode": os.getenv("TEST_DB_SSL_MODE", "disable"),
        "additional_params": {
            "pool_size": int(os.getenv("TEST_DB_POOL_SIZE", "5")),
            "max_overflow": int(os.getenv("TEST_DB_MAX_OVERFLOW", "10"))
        }
    }


@pytest.fixture
def server_health_check(api_base_url, http_client):
    """Check if the API server is running."""
    try:
        response = http_client.get(f"{api_base_url}/dbmcp/health")
        return response.status_code == 200
    except httpx.ConnectError:
        return False


@pytest.fixture
def require_server_running(server_health_check):
    """Skip tests if server is not running."""
    if not server_health_check:
        pytest.skip("API server at http://localhost:8000 is not running. Please start the server first.") 