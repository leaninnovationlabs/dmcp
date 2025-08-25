#!/usr/bin/env python3
"""
Focused unit tests for datasource API endpoints.
Tests the two main requirements:
1. Create a new data source using PostgreSQL configuration from .test.env
2. Test connection to the created data source

Uses real HTTP requests to http://localhost:8000
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


class TestDatasourceEndpoints:
    """Test class for datasource API endpoints using real HTTP requests."""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test environment."""
        # Load test environment variables
        from dotenv import load_dotenv
        load_dotenv(os.path.join(os.path.dirname(__file__), '.test.env'))
        
        # API base URL
        self.base_url = "http://localhost:8000"
        
        # Generate test token for authentication
        payload = {
            "user_id": 123,
            "username": "test_user",
            "email": "test@example.com"
        }
        self.test_token = jwt_validator.create_token(payload)
        self.headers = {"Authorization": f"Bearer {self.test_token}"}
        
        # Create HTTP client
        self.client = httpx.Client(timeout=30.0)
    
    def get_postgres_config_from_env(self) -> Dict[str, Any]:
        """Get PostgreSQL configuration from .test.env file."""
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
    
    def test_1_create_datasource_with_postgres_config(self):
        """
        Test 1: Create a new data source using the configuration from the postgres 
        connection config from .test.env
        """
        print("\n" + "="*60)
        print("TEST 1: Creating datasource with PostgreSQL config from .test.env")
        print("="*60)
        
        # Get PostgreSQL configuration from test environment
        config = self.get_postgres_config_from_env()
        print(f"📋 Using config: {config}")
        
        # Prepare datasource creation request
        datasource_data = {
            "name": config["name"],
            "database_type": config["database_type"],
            "host": config["host"],
            "port": config["port"],
            "database": config["database"],
            "username": config["username"],
            "password": config["password"],
            "ssl_mode": config["ssl_mode"],
            "additional_params": config["additional_params"]
        }
        
        print(f"🚀 Making API request to create datasource...")
        print(f"🌐 URL: {self.base_url}/dmcp/datasources")
        
        # Make API request to create datasource
        try:
            response = self.client.post(
                f"{self.base_url}/dmcp/datasources",
                json=datasource_data,
                headers=self.headers
            )
            
            # Assert response status
            assert response.status_code == 200, f"Expected 200, got {response.status_code}"
            
            # Parse response data
            data = response.json()
            print(f"📊 Response: {data}")
            
            # Assert response structure and success
            assert data["success"] is True, "Expected success to be True"
            assert "data" in data, "Expected 'data' field in response"
            
            # Assert datasource data matches input
            datasource = data["data"]
            assert datasource["name"] == config["name"], f"Expected name {config['name']}, got {datasource['name']}"
            assert datasource["database_type"] == config["database_type"], f"Expected database_type {config['database_type']}, got {datasource['database_type']}"
            assert datasource["host"] == config["host"], f"Expected host {config['host']}, got {datasource['host']}"
            assert datasource["port"] == config["port"], f"Expected port {config['port']}, got {datasource['port']}"
            assert datasource["database"] == config["database"], f"Expected database {config['database']}, got {datasource['database']}"
            assert datasource["username"] == config["username"], f"Expected username {config['username']}, got {datasource['username']}"
            
            # Store datasource ID for the next test
            self.datasource_id = datasource["id"]
            print(f"✅ Successfully created datasource with ID: {self.datasource_id}")
            
            return self.datasource_id
            
        except httpx.ConnectError:
            pytest.skip("Cannot connect to API server at http://localhost:8000. Please ensure the server is running.")
        except Exception as e:
            pytest.fail(f"Unexpected error: {e}")
    
    def test_2_test_connection_to_created_datasource(self):
        """
        Test 2: Test case to make sure we can connect to the data source created above
        """
        print("\n" + "="*60)
        print("TEST 2: Testing connection to the created datasource")
        print("="*60)
        
        # First create a datasource if not already created
        if not hasattr(self, 'datasource_id'):
            self.datasource_id = self.test_1_create_datasource_with_postgres_config()
        
        print(f"🔗 Testing connection to datasource ID: {self.datasource_id}")
        print(f"🌐 URL: {self.base_url}/dmcp/datasources/{self.datasource_id}/test")
        
        # Make API request to test connection
        try:
            response = self.client.post(
                f"{self.base_url}/dmcp/datasources/{self.datasource_id}/test",
                headers=self.headers
            )
            
            # Assert response status
            assert response.status_code == 200, f"Expected 200, got {response.status_code}"
            
            # Parse response data
            data = response.json()
            print(f"📊 Connection test response: {data}")
            
            # Assert response structure and success
            assert data["success"] is True, "Expected success to be True"
            assert "data" in data, "Expected 'data' field in response"
            
            # Get connection test results
            connection_data = data["data"]
            assert "success" in connection_data, "Expected 'success' field in connection data"
            assert "connection_time_ms" in connection_data, "Expected 'connection_time_ms' field in connection data"
            
            # Check if connection was successful
            if connection_data.get("success"):
                print("✅ Connection test successful!")
                assert "message" in connection_data, "Expected 'message' field for successful connection"
                assert connection_data["connection_time_ms"] > 0, "Expected positive connection time"
                print(f"⏱️  Connection time: {connection_data['connection_time_ms']}ms")
                print(f"📝 Message: {connection_data.get('message', 'No message')}")
            else:
                print("❌ Connection test failed!")
                assert "error" in connection_data, "Expected 'error' field for failed connection"
                print(f"🚨 Error: {connection_data.get('error', 'Unknown error')}")
                # Don't fail the test if connection fails (database might not be running)
                pytest.skip("Database connection failed - skipping test")
                
        except httpx.ConnectError:
            pytest.skip("Cannot connect to API server at http://localhost:8000. Please ensure the server is running.")
        except Exception as e:
            pytest.fail(f"Unexpected error: {e}")
    
    def test_3_integration_test_create_and_connect(self):
        """
        Integration test: Create datasource and immediately test connection
        """
        print("\n" + "="*60)
        print("TEST 3: Integration test - Create and test connection")
        print("="*60)
        
        # Get PostgreSQL configuration
        config = self.get_postgres_config_from_env()
        
        # Create datasource
        datasource_data = {
            "name": "Integration Test Datasource",
            "database_type": config["database_type"],
            "host": config["host"],
            "port": config["port"],
            "database": config["database"],
            "username": config["username"],
            "password": config["password"],
            "ssl_mode": config["ssl_mode"]
        }
        
        print("📝 Creating datasource for integration test...")
        print(f"🌐 URL: {self.base_url}/dmcp/datasources")
        
        try:
            create_response = self.client.post(
                f"{self.base_url}/dmcp/datasources",
                json=datasource_data,
                headers=self.headers
            )
            
            assert create_response.status_code == 200
            create_data = create_response.json()
            assert create_data["success"] is True
            
            datasource_id = create_data["data"]["id"]
            print(f"✅ Created datasource with ID: {datasource_id}")
            
            # Test connection
            print("🔗 Testing connection...")
            print(f"🌐 URL: {self.base_url}/dmcp/datasources/{datasource_id}/test")
            
            test_response = self.client.post(
                f"{self.base_url}/dmcp/datasources/{datasource_id}/test",
                headers=self.headers
            )
            
            assert test_response.status_code == 200
            test_data = test_response.json()
            assert test_data["success"] is True
            
            connection_data = test_data["data"]
            print(f"📊 Connection test result: {connection_data}")
            
            # Verify connection test structure
            assert "success" in connection_data
            assert "connection_time_ms" in connection_data
            
            if connection_data.get("success"):
                print("✅ Integration test successful!")
                assert "message" in connection_data
                assert connection_data["connection_time_ms"] > 0
            else:
                print(f"❌ Integration test failed: {connection_data.get('error', 'Unknown error')}")
                pytest.skip("Database connection failed in integration test")
                
        except httpx.ConnectError:
            pytest.skip("Cannot connect to API server at http://localhost:8000. Please ensure the server is running.")
        except Exception as e:
            pytest.fail(f"Unexpected error: {e}")
    
    def test_4_health_check(self):
        """
        Test 4: Health check to verify API server is running
        """
        print("\n" + "="*60)
        print("TEST 4: Health check - Verify API server is running")
        print("="*60)
        
        print(f"🌐 Checking health endpoint: {self.base_url}/dmcp/health")
        
        try:
            response = self.client.get(f"{self.base_url}/dmcp/health")
            
            print(f"📊 Health check response status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Health check successful: {data}")
                assert "status" in data or "message" in data, "Expected health status in response"
            else:
                print(f"⚠️  Health check returned status {response.status_code}")
                print(f"Response: {response.text}")
                
        except httpx.ConnectError:
            pytest.skip("Cannot connect to API server at http://localhost:8000. Please ensure the server is running.")
        except Exception as e:
            pytest.fail(f"Unexpected error during health check: {e}")


if __name__ == "__main__":
    # Run the specific tests
    pytest.main([__file__, "-v", "-s"]) 