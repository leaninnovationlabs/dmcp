#!/usr/bin/env python3
"""
Unit tests for datasource API endpoints.
Tests include creating datasources and testing connections.
Uses real HTTP requests to http://localhost:8000
"""

import os

# Add the app directory to Python path
import sys
from typing import Any, Dict

import httpx
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.core.jwt_validator import jwt_validator
from app.models.schemas import DatabaseType


class TestDatasourceAPI:
    """Test class for datasource API endpoints using real HTTP requests."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test environment."""
        # Load test environment variables
        from dotenv import load_dotenv

        load_dotenv(os.path.join(os.path.dirname(__file__), ".test.env"))

        # API base URL
        self.base_url = "http://localhost:8000"

        # Generate test token
        payload = {"user_id": 123, "username": "test_user", "email": "test@example.com"}
        self.test_token = jwt_validator.create_token(payload)
        self.headers = {"Authorization": f"Bearer {self.test_token}"}

        # Create HTTP client
        self.client = httpx.Client(timeout=30.0)

    def get_postgres_config(self) -> Dict[str, Any]:
        """Get PostgreSQL configuration from test environment."""
        return {
            "name": "Test PostgreSQL Database",
            "database_type": DatabaseType.POSTGRESQL,
            "host": os.getenv("TEST_DB_HOST", "localhost"),
            "port": int(os.getenv("TEST_DB_PORT", "5432")),
            "database": os.getenv("TEST_DB_NAME", "test_db"),
            "username": os.getenv("TEST_DB_USER", "postgres"),
            "password": os.getenv("TEST_DB_PASSWORD", "password"),
            "ssl_mode": os.getenv("TEST_DB_SSL_MODE", "disable"),
            "additional_params": {
                "pool_size": int(os.getenv("TEST_DB_POOL_SIZE", "5")),
                "max_overflow": int(os.getenv("TEST_DB_MAX_OVERFLOW", "10")),
            },
        }

    def test_create_datasource_success(self):
        """Test creating a new datasource with valid PostgreSQL configuration."""
        config = self.get_postgres_config()

        # Create datasource request
        datasource_data = {
            "name": config["name"],
            "database_type": config["database_type"].value,
            "host": config["host"],
            "port": config["port"],
            "database": config["database"],
            "username": config["username"],
            "password": config["password"],
            "ssl_mode": config["ssl_mode"],
            "additional_params": config["additional_params"],
        }

        try:
            # Make API request
            response = self.client.post(
                f"{self.base_url}/dmcp/datasources",
                json=datasource_data,
                headers=self.headers,
            )

            # Assert response
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert "data" in data
            assert data["data"]["name"] == config["name"]
            assert data["data"]["database_type"] == config["database_type"].value
            assert data["data"]["host"] == config["host"]
            assert data["data"]["port"] == config["port"]
            assert data["data"]["database"] == config["database"]
            assert data["data"]["username"] == config["username"]

            # Store datasource ID for connection test
            self.datasource_id = data["data"]["id"]

        except httpx.ConnectError:
            pytest.skip(
                "Cannot connect to API server at http://localhost:8000. Please ensure the server is running."
            )
        except Exception as e:
            pytest.fail(f"Unexpected error: {e}")

    def test_create_datasource_without_auth(self):
        """Test creating a datasource without authentication should fail."""
        config = self.get_postgres_config()
        datasource_data = {
            "name": "Unauthorized Test",
            "database_type": config["database_type"].value,
            "host": config["host"],
            "port": config["port"],
            "database": config["database"],
            "username": config["username"],
            "password": config["password"],
        }

        try:
            response = self.client.post(
                f"{self.base_url}/dmcp/datasources", json=datasource_data
            )

            assert response.status_code == 401

        except httpx.ConnectError:
            pytest.skip(
                "Cannot connect to API server at http://localhost:8000. Please ensure the server is running."
            )
        except Exception as e:
            pytest.fail(f"Unexpected error: {e}")

    def test_create_datasource_invalid_data(self):
        """Test creating a datasource with invalid data should fail."""
        invalid_data = {
            "name": "",  # Empty name
            "database_type": "invalid_type",
            "database": "test_db",
        }

        try:
            response = self.client.post(
                f"{self.base_url}/dmcp/datasources",
                json=invalid_data,
                headers=self.headers,
            )

            assert response.status_code == 200  # API returns 200 with error in response
            data = response.json()
            assert data["success"] is False
            assert len(data["errors"]) > 0

        except httpx.ConnectError:
            pytest.skip(
                "Cannot connect to API server at http://localhost:8000. Please ensure the server is running."
            )
        except Exception as e:
            pytest.fail(f"Unexpected error: {e}")

    def test_list_datasources(self):
        """Test listing all datasources."""
        try:
            response = self.client.get(
                f"{self.base_url}/dmcp/datasources", headers=self.headers
            )

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert "data" in data
            assert isinstance(data["data"], list)

        except httpx.ConnectError:
            pytest.skip(
                "Cannot connect to API server at http://localhost:8000. Please ensure the server is running."
            )
        except Exception as e:
            pytest.fail(f"Unexpected error: {e}")

    def test_list_datasources_without_auth(self):
        """Test listing datasources without authentication should fail."""
        try:
            response = self.client.get(f"{self.base_url}/dmcp/datasources")

            assert response.status_code == 401

        except httpx.ConnectError:
            pytest.skip(
                "Cannot connect to API server at http://localhost:8000. Please ensure the server is running."
            )
        except Exception as e:
            pytest.fail(f"Unexpected error: {e}")

    def test_get_datasource_by_id(self):
        """Test getting a specific datasource by ID."""
        # First create a datasource
        config = self.get_postgres_config()
        datasource_data = {
            "name": "Test Get Datasource",
            "database_type": config["database_type"].value,
            "host": config["host"],
            "port": config["port"],
            "database": config["database"],
            "username": config["username"],
            "password": config["password"],
        }

        try:
            create_response = self.client.post(
                f"{self.base_url}/dmcp/datasources",
                json=datasource_data,
                headers=self.headers,
            )

            assert create_response.status_code == 200
            created_datasource = create_response.json()["data"]
            datasource_id = created_datasource["id"]

            # Now get the datasource by ID
            response = self.client.get(
                f"{self.base_url}/dmcp/datasources/{datasource_id}",
                headers=self.headers,
            )

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["data"]["id"] == datasource_id
            assert data["data"]["name"] == "Test Get Datasource"

        except httpx.ConnectError:
            pytest.skip(
                "Cannot connect to API server at http://localhost:8000. Please ensure the server is running."
            )
        except Exception as e:
            pytest.fail(f"Unexpected error: {e}")

    def test_get_nonexistent_datasource(self):
        """Test getting a datasource that doesn't exist."""
        try:
            response = self.client.get(
                f"{self.base_url}/dmcp/datasources/99999", headers=self.headers
            )

            assert response.status_code == 200  # API returns 200 with error in response
            data = response.json()
            assert data["success"] is False
            assert "Datasource not found" in str(data["errors"])

        except httpx.ConnectError:
            pytest.skip(
                "Cannot connect to API server at http://localhost:8000. Please ensure the server is running."
            )
        except Exception as e:
            pytest.fail(f"Unexpected error: {e}")

    def test_test_datasource_connection(self):
        """Test testing connection to a datasource."""
        # First create a datasource
        config = self.get_postgres_config()
        datasource_data = {
            "name": "Test Connection Datasource",
            "database_type": config["database_type"].value,
            "host": config["host"],
            "port": config["port"],
            "database": config["database"],
            "username": config["username"],
            "password": config["password"],
        }

        try:
            create_response = self.client.post(
                f"{self.base_url}/dmcp/datasources",
                json=datasource_data,
                headers=self.headers,
            )

            assert create_response.status_code == 200
            created_datasource = create_response.json()["data"]
            datasource_id = created_datasource["id"]

            # Test the connection
            response = self.client.post(
                f"{self.base_url}/dmcp/datasources/{datasource_id}/test",
                headers=self.headers,
            )

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert "data" in data

            # The connection test should return connection details
            connection_data = data["data"]
            assert "success" in connection_data
            assert "connection_time_ms" in connection_data

            # If connection is successful, these should be present
            if connection_data.get("success"):
                assert "message" in connection_data
            else:
                assert "error" in connection_data

        except httpx.ConnectError:
            pytest.skip(
                "Cannot connect to API server at http://localhost:8000. Please ensure the server is running."
            )
        except Exception as e:
            pytest.fail(f"Unexpected error: {e}")

    def test_test_connection_nonexistent_datasource(self):
        """Test testing connection for a datasource that doesn't exist."""
        try:
            response = self.client.post(
                f"{self.base_url}/dmcp/datasources/99999/test", headers=self.headers
            )

            assert response.status_code == 200  # API returns 200 with error in response
            data = response.json()
            assert data["success"] is False
            assert len(data["errors"]) > 0

        except httpx.ConnectError:
            pytest.skip(
                "Cannot connect to API server at http://localhost:8000. Please ensure the server is running."
            )
        except Exception as e:
            pytest.fail(f"Unexpected error: {e}")

    def test_update_datasource(self):
        """Test updating a datasource."""
        # First create a datasource
        config = self.get_postgres_config()
        datasource_data = {
            "name": "Test Update Datasource",
            "database_type": config["database_type"].value,
            "host": config["host"],
            "port": config["port"],
            "database": config["database"],
            "username": config["username"],
            "password": config["password"],
        }

        try:
            create_response = self.client.post(
                f"{self.base_url}/dmcp/datasources",
                json=datasource_data,
                headers=self.headers,
            )

            assert create_response.status_code == 200
            created_datasource = create_response.json()["data"]
            datasource_id = created_datasource["id"]

            # Update the datasource
            update_data = {
                "name": "Updated Test Datasource",
                "port": 5433,  # Change port
            }

            response = self.client.put(
                f"{self.base_url}/dmcp/datasources/{datasource_id}",
                json=update_data,
                headers=self.headers,
            )

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["data"]["name"] == "Updated Test Datasource"
            assert data["data"]["port"] == 5433

        except httpx.ConnectError:
            pytest.skip(
                "Cannot connect to API server at http://localhost:8000. Please ensure the server is running."
            )
        except Exception as e:
            pytest.fail(f"Unexpected error: {e}")

    def test_delete_datasource(self):
        """Test deleting a datasource."""
        # First create a datasource
        config = self.get_postgres_config()
        datasource_data = {
            "name": "Test Delete Datasource",
            "database_type": config["database_type"].value,
            "host": config["host"],
            "port": config["port"],
            "database": config["database"],
            "username": config["username"],
            "password": config["password"],
        }

        try:
            create_response = self.client.post(
                f"{self.base_url}/dmcp/datasources",
                json=datasource_data,
                headers=self.headers,
            )

            assert create_response.status_code == 200
            created_datasource = create_response.json()["data"]
            datasource_id = created_datasource["id"]

            # Delete the datasource
            response = self.client.delete(
                f"{self.base_url}/dmcp/datasources/{datasource_id}",
                headers=self.headers,
            )

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert "message" in data["data"]
            assert "deleted successfully" in data["data"]["message"]

            # Verify the datasource is deleted
            get_response = self.client.get(
                f"{self.base_url}/dmcp/datasources/{datasource_id}",
                headers=self.headers,
            )

            assert get_response.status_code == 200
            get_data = get_response.json()
            assert get_data["success"] is False
            assert "Datasource not found" in str(get_data["errors"])

        except httpx.ConnectError:
            pytest.skip(
                "Cannot connect to API server at http://localhost:8000. Please ensure the server is running."
            )
        except Exception as e:
            pytest.fail(f"Unexpected error: {e}")

    def test_delete_nonexistent_datasource(self):
        """Test deleting a datasource that doesn't exist."""
        try:
            response = self.client.delete(
                f"{self.base_url}/dmcp/datasources/99999", headers=self.headers
            )

            assert response.status_code == 200  # API returns 200 with error in response
            data = response.json()
            assert data["success"] is False
            assert "Datasource not found" in str(data["errors"])

        except httpx.ConnectError:
            pytest.skip(
                "Cannot connect to API server at http://localhost:8000. Please ensure the server is running."
            )
        except Exception as e:
            pytest.fail(f"Unexpected error: {e}")


class TestDatasourceConnection:
    """Test class specifically for datasource connection testing."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test environment."""
        from dotenv import load_dotenv

        load_dotenv(os.path.join(os.path.dirname(__file__), ".test.env"))

        # API base URL
        self.base_url = "http://localhost:8000"

        # Generate test token
        payload = {"user_id": 123, "username": "test_user", "email": "test@example.com"}
        self.test_token = jwt_validator.create_token(payload)
        self.headers = {"Authorization": f"Bearer {self.test_token}"}

        # Create HTTP client
        self.client = httpx.Client(timeout=30.0)

    def get_postgres_config(self) -> Dict[str, Any]:
        """Get PostgreSQL configuration from test environment."""
        return {
            "name": "PostgreSQL Connection Test",
            "database_type": DatabaseType.POSTGRESQL,
            "host": os.getenv("TEST_DB_HOST", "localhost"),
            "port": int(os.getenv("TEST_DB_PORT", "5432")),
            "database": os.getenv("TEST_DB_NAME", "test_db"),
            "username": os.getenv("TEST_DB_USER", "postgres"),
            "password": os.getenv("TEST_DB_PASSWORD", "password"),
            "ssl_mode": os.getenv("TEST_DB_SSL_MODE", "disable"),
        }

    def test_create_and_test_connection(self):
        """Test creating a datasource and then testing its connection."""
        # Step 1: Create a datasource using PostgreSQL config
        config = self.get_postgres_config()
        datasource_data = {
            "name": config["name"],
            "database_type": config["database_type"].value,
            "host": config["host"],
            "port": config["port"],
            "database": config["database"],
            "username": config["username"],
            "password": config["password"],
            "ssl_mode": config["ssl_mode"],
        }

        try:
            # Create the datasource
            create_response = self.client.post(
                f"{self.base_url}/dmcp/datasources",
                json=datasource_data,
                headers=self.headers,
            )

            assert create_response.status_code == 200
            create_data = create_response.json()
            assert create_data["success"] is True

            datasource_id = create_data["data"]["id"]
            print(f"✅ Created datasource with ID: {datasource_id}")

            # Step 2: Test the connection to the created datasource
            test_response = self.client.post(
                f"{self.base_url}/dmcp/datasources/{datasource_id}/test",
                headers=self.headers,
            )

            assert test_response.status_code == 200
            test_data = test_response.json()
            assert test_data["success"] is True

            connection_data = test_data["data"]
            print(f"🔗 Connection test result: {connection_data}")

            # Verify connection test response structure
            assert "success" in connection_data
            assert "connection_time_ms" in connection_data

            if connection_data.get("success"):
                print("✅ Connection test successful!")
                assert "message" in connection_data
                assert connection_data["connection_time_ms"] > 0
            else:
                print(
                    f"❌ Connection test failed: {connection_data.get('error', 'Unknown error')}"
                )
                assert "error" in connection_data

        except httpx.ConnectError:
            pytest.skip(
                "Cannot connect to API server at http://localhost:8000. Please ensure the server is running."
            )
        except Exception as e:
            pytest.fail(f"Unexpected error: {e}")

    def test_connection_with_invalid_credentials(self):
        """Test connection with invalid database credentials."""
        config = self.get_postgres_config()
        datasource_data = {
            "name": "Invalid Credentials Test",
            "database_type": config["database_type"].value,
            "host": config["host"],
            "port": config["port"],
            "database": config["database"],
            "username": "invalid_user",
            "password": "invalid_password",
            "ssl_mode": config["ssl_mode"],
        }

        try:
            # Create datasource with invalid credentials
            create_response = self.client.post(
                f"{self.base_url}/dmcp/datasources",
                json=datasource_data,
                headers=self.headers,
            )

            assert create_response.status_code == 200
            create_data = create_response.json()
            assert create_data["success"] is True

            datasource_id = create_data["data"]["id"]

            # Test connection (should fail)
            test_response = self.client.post(
                f"{self.base_url}/dmcp/datasources/{datasource_id}/test",
                headers=self.headers,
            )

            assert test_response.status_code == 200
            test_data = test_response.json()
            assert test_data["success"] is True

            connection_data = test_data["data"]
            # Connection should fail with invalid credentials
            assert connection_data.get("success") is False
            assert "error" in connection_data

        except httpx.ConnectError:
            pytest.skip(
                "Cannot connect to API server at http://localhost:8000. Please ensure the server is running."
            )
        except Exception as e:
            pytest.fail(f"Unexpected error: {e}")


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
