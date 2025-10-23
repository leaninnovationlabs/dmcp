#!/usr/bin/env python3
"""
Unit tests for tool search API endpoint.
Tests include searching tools by name and description with case-insensitive matching.
Uses real HTTP requests to http://localhost:8000
"""

import os
import sys
from typing import Any, Dict

import httpx
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.core.jwt_validator import jwt_validator
from app.models.schemas import DatabaseType


class TestToolSearchAPI:
    """Test class for tool search API endpoint using real HTTP requests."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test environment."""
        from dotenv import load_dotenv

        load_dotenv(os.path.join(os.path.dirname(__file__), ".test.env"))

        self.base_url = "http://localhost:8000"

        payload = {"user_id": 123, "username": "test_user", "email": "test@example.com"}
        self.test_token = jwt_validator.create_token(payload)
        self.headers = {"Authorization": f"Bearer {self.test_token}"}

        self.client = httpx.Client(timeout=30.0)

        self.created_datasource_id = None
        self.created_tool_ids = []

    def get_postgres_config(self) -> Dict[str, Any]:
        """Get PostgreSQL configuration from test environment."""
        return {
            "name": "Test Search Database",
            "database_type": DatabaseType.POSTGRESQL,
            "host": os.getenv("TEST_DB_HOST", "localhost"),
            "port": int(os.getenv("TEST_DB_PORT", "5432")),
            "database": os.getenv("TEST_DB_NAME", "test_db"),
            "username": os.getenv("TEST_DB_USER", "postgres"),
            "password": os.getenv("TEST_DB_PASSWORD", "password"),
            "ssl_mode": os.getenv("TEST_DB_SSL_MODE", "disable"),
        }

    def create_test_datasource(self) -> int:
        """Create a test datasource and return its ID."""
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

        response = self.client.post(
            f"{self.base_url}/dmcp/datasources",
            json=datasource_data,
            headers=self.headers,
        )

        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                return data["data"]["id"]
        return None

    def create_test_tool(self, name: str, description: str, sql: str) -> int:
        """Create a test tool and return its ID."""
        if not self.created_datasource_id:
            self.created_datasource_id = self.create_test_datasource()

        tool_data = {
            "name": name,
            "description": description,
            "type": "query",
            "sql": sql,
            "datasource_id": self.created_datasource_id,
            "parameters": [],
            "tags": [],
        }

        response = self.client.post(
            f"{self.base_url}/dmcp/tools",
            json=tool_data,
            headers=self.headers,
        )

        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                tool_id = data["data"]["id"]
                self.created_tool_ids.append(tool_id)
                return tool_id
        return None

    def test_search_tools_by_name(self):
        """Test searching tools by name."""
        try:
            self.create_test_tool(
                "get_user_data",
                "Retrieves user information from database",
                "SELECT * FROM users WHERE id = {{ user_id }}"
            )
            self.create_test_tool(
                "get_order_data",
                "Retrieves order information",
                "SELECT * FROM orders WHERE id = {{ order_id }}"
            )

            response = self.client.get(
                f"{self.base_url}/dmcp/tools/search?q=user",
                headers=self.headers,
            )

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert "data" in data
            assert isinstance(data["data"], list)
            assert len(data["data"]) >= 1

            tool_names = [tool["name"] for tool in data["data"]]
            assert "get_user_data" in tool_names

        except httpx.ConnectError:
            pytest.skip("Cannot connect to API server at http://localhost:8000. Please ensure the server is running.")
        except Exception as e:
            pytest.fail(f"Unexpected error: {e}")

    def test_search_tools_by_description(self):
        """Test searching tools by description."""
        try:
            self.create_test_tool(
                "calculate_cost",
                "Calculates the total cost of items",
                "SELECT SUM(price) FROM items"
            )

            response = self.client.get(
                f"{self.base_url}/dmcp/tools/search?q=cost",
                headers=self.headers,
            )

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert len(data["data"]) >= 1

            found = False
            for tool in data["data"]:
                if "cost" in tool["description"].lower():
                    found = True
                    break
            assert found

        except httpx.ConnectError:
            pytest.skip("Cannot connect to API server at http://localhost:8000. Please ensure the server is running.")
        except Exception as e:
            pytest.fail(f"Unexpected error: {e}")

    def test_search_tools_case_insensitive(self):
        """Test that search is case-insensitive."""
        try:
            self.create_test_tool(
                "get_AWS_resources",
                "Retrieves AWS resource information",
                "SELECT * FROM aws_resources"
            )

            response_upper = self.client.get(
                f"{self.base_url}/dmcp/tools/search?q=AWS",
                headers=self.headers,
            )
            response_lower = self.client.get(
                f"{self.base_url}/dmcp/tools/search?q=aws",
                headers=self.headers,
            )
            response_mixed = self.client.get(
                f"{self.base_url}/dmcp/tools/search?q=Aws",
                headers=self.headers,
            )

            assert response_upper.status_code == 200
            assert response_lower.status_code == 200
            assert response_mixed.status_code == 200

            data_upper = response_upper.json()
            data_lower = response_lower.json()
            data_mixed = response_mixed.json()

            assert data_upper["success"] is True
            assert data_lower["success"] is True
            assert data_mixed["success"] is True

            assert len(data_upper["data"]) == len(data_lower["data"])
            assert len(data_upper["data"]) == len(data_mixed["data"])

        except httpx.ConnectError:
            pytest.skip("Cannot connect to API server at http://localhost:8000. Please ensure the server is running.")
        except Exception as e:
            pytest.fail(f"Unexpected error: {e}")

    def test_search_tools_partial_match(self):
        """Test that search supports partial matching."""
        try:
            self.create_test_tool(
                "get_customer_orders",
                "Retrieves customer order history",
                "SELECT * FROM orders WHERE customer_id = {{ customer_id }}"
            )

            response = self.client.get(
                f"{self.base_url}/dmcp/tools/search?q=cust",
                headers=self.headers,
            )

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert len(data["data"]) >= 1

            found = False
            for tool in data["data"]:
                if "customer" in tool["name"].lower() or "customer" in tool["description"].lower():
                    found = True
                    break
            assert found

        except httpx.ConnectError:
            pytest.skip("Cannot connect to API server at http://localhost:8000. Please ensure the server is running.")
        except Exception as e:
            pytest.fail(f"Unexpected error: {e}")

    def test_search_tools_no_results(self):
        """Test search with query that returns no results."""
        try:
            response = self.client.get(
                f"{self.base_url}/dmcp/tools/search?q=nonexistentquerystringxyz123",
                headers=self.headers,
            )

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert isinstance(data["data"], list)
            assert len(data["data"]) == 0

        except httpx.ConnectError:
            pytest.skip("Cannot connect to API server at http://localhost:8000. Please ensure the server is running.")
        except Exception as e:
            pytest.fail(f"Unexpected error: {e}")

    def test_search_tools_empty_query(self):
        """Test search with empty query string."""
        try:
            response = self.client.get(
                f"{self.base_url}/dmcp/tools/search?q=",
                headers=self.headers,
            )

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is False
            assert len(data["errors"]) > 0

        except httpx.ConnectError:
            pytest.skip("Cannot connect to API server at http://localhost:8000. Please ensure the server is running.")
        except Exception as e:
            pytest.fail(f"Unexpected error: {e}")

    def test_search_tools_whitespace_only_query(self):
        """Test search with whitespace-only query."""
        try:
            response = self.client.get(
                f"{self.base_url}/dmcp/tools/search?q=   ",
                headers=self.headers,
            )

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is False
            assert len(data["errors"]) > 0

        except httpx.ConnectError:
            pytest.skip("Cannot connect to API server at http://localhost:8000. Please ensure the server is running.")
        except Exception as e:
            pytest.fail(f"Unexpected error: {e}")

    def test_search_tools_without_auth(self):
        """Test search without authentication should fail."""
        try:
            response = self.client.get(f"{self.base_url}/dmcp/tools/search?q=test")

            assert response.status_code == 401

        except httpx.ConnectError:
            pytest.skip("Cannot connect to API server at http://localhost:8000. Please ensure the server is running.")
        except Exception as e:
            pytest.fail(f"Unexpected error: {e}")

    def test_search_tools_multiple_results(self):
        """Test search that returns multiple results."""
        try:
            self.create_test_tool(
                "get_product_info",
                "Retrieves product information",
                "SELECT * FROM products WHERE id = {{ product_id }}"
            )
            self.create_test_tool(
                "get_product_price",
                "Gets product pricing data",
                "SELECT price FROM products WHERE id = {{ product_id }}"
            )
            self.create_test_tool(
                "list_products",
                "Lists all available products",
                "SELECT * FROM products"
            )

            response = self.client.get(
                f"{self.base_url}/dmcp/tools/search?q=product",
                headers=self.headers,
            )

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert len(data["data"]) >= 3

            product_tools = [tool for tool in data["data"] if "product" in tool["name"].lower()]
            assert len(product_tools) >= 3

        except httpx.ConnectError:
            pytest.skip("Cannot connect to API server at http://localhost:8000. Please ensure the server is running.")
        except Exception as e:
            pytest.fail(f"Unexpected error: {e}")

    def test_search_tools_special_characters(self):
        """Test search with special characters."""
        try:
            response = self.client.get(
                f"{self.base_url}/dmcp/tools/search?q=test%20query",
                headers=self.headers,
            )

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True

        except httpx.ConnectError:
            pytest.skip("Cannot connect to API server at http://localhost:8000. Please ensure the server is running.")
        except Exception as e:
            pytest.fail(f"Unexpected error: {e}")

    def test_search_tools_long_query(self):
        """Test search with very long query string."""
        try:
            long_query = "a" * 300

            response = self.client.get(
                f"{self.base_url}/dmcp/tools/search?q={long_query}",
                headers=self.headers,
            )

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is False
            assert len(data["errors"]) > 0

        except httpx.ConnectError:
            pytest.skip("Cannot connect to API server at http://localhost:8000. Please ensure the server is running.")
        except Exception as e:
            pytest.fail(f"Unexpected error: {e}")
