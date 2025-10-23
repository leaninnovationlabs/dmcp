#!/usr/bin/env python3
"""
Unit tests for tool search API endpoint.
Tests include repository, service, and integration tests for the search functionality.
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

        self.datasource_id = None
        self.tool_ids = []

    def get_postgres_config(self) -> Dict[str, Any]:
        """Get PostgreSQL configuration from test environment."""
        return {
            "name": "Test PostgreSQL for Search",
            "database_type": DatabaseType.POSTGRESQL,
            "host": os.getenv("TEST_DB_HOST", "localhost"),
            "port": int(os.getenv("TEST_DB_PORT", "5432")),
            "database": os.getenv("TEST_DB_NAME", "test_db"),
            "username": os.getenv("TEST_DB_USER", "postgres"),
            "password": os.getenv("TEST_DB_PASSWORD", "password"),
            "ssl_mode": os.getenv("TEST_DB_SSL_MODE", "disable"),
        }

    def create_test_datasource(self):
        """Create a test datasource for tool tests."""
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
            response = self.client.post(
                f"{self.base_url}/dmcp/datasources",
                json=datasource_data,
                headers=self.headers,
            )

            if response.status_code == 200:
                data = response.json()
                if data["success"]:
                    self.datasource_id = data["data"]["id"]
                    return self.datasource_id
        except Exception:
            pass

        return None

    def create_test_tool(self, name: str, description: str, sql: str = "SELECT 1"):
        """Create a test tool."""
        if not self.datasource_id:
            self.create_test_datasource()

        tool_data = {
            "name": name,
            "description": description,
            "type": "query",
            "sql": sql,
            "datasource_id": self.datasource_id,
            "parameters": [],
            "tags": [],
        }

        try:
            response = self.client.post(
                f"{self.base_url}/dmcp/tools",
                json=tool_data,
                headers=self.headers,
            )

            if response.status_code == 200:
                data = response.json()
                if data["success"]:
                    tool_id = data["data"]["id"]
                    self.tool_ids.append(tool_id)
                    return tool_id
        except Exception:
            pass

        return None

    def cleanup_test_tools(self):
        """Clean up test tools created during tests."""
        for tool_id in self.tool_ids:
            try:
                self.client.delete(
                    f"{self.base_url}/dmcp/tools/{tool_id}",
                    headers=self.headers,
                )
            except Exception:
                pass

        if self.datasource_id:
            try:
                self.client.delete(
                    f"{self.base_url}/dmcp/datasources/{self.datasource_id}",
                    headers=self.headers,
                )
            except Exception:
                pass

    def test_search_tools_basic(self):
        """Test basic tool search functionality."""
        self.create_test_tool("user_query", "Get all users from database", "SELECT * FROM users")
        self.create_test_tool("product_query", "Get all products", "SELECT * FROM products")
        self.create_test_tool("order_query", "Get all orders", "SELECT * FROM orders")

        try:
            response = self.client.get(
                f"{self.base_url}/dmcp/tools/search",
                params={"q": "user"},
                headers=self.headers,
            )

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert "data" in data

            search_result = data["data"]
            assert "tools" in search_result
            assert "total_count" in search_result
            assert "limit" in search_result
            assert "offset" in search_result
            assert "has_more" in search_result

            assert len(search_result["tools"]) >= 1
            assert any("user" in tool["name"].lower() for tool in search_result["tools"])

        except httpx.ConnectError:
            pytest.skip("Cannot connect to API server. Please ensure the server is running.")
        except Exception as e:
            pytest.fail(f"Unexpected error: {e}")
        finally:
            self.cleanup_test_tools()

    def test_search_tools_case_insensitive(self):
        """Test case-insensitive search."""
        self.create_test_tool("UserQuery", "Get Users", "SELECT * FROM users")

        try:
            response = self.client.get(
                f"{self.base_url}/dmcp/tools/search",
                params={"q": "user"},
                headers=self.headers,
            )

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True

            search_result = data["data"]
            assert len(search_result["tools"]) >= 1

            response_upper = self.client.get(
                f"{self.base_url}/dmcp/tools/search",
                params={"q": "USER"},
                headers=self.headers,
            )

            assert response_upper.status_code == 200
            data_upper = response_upper.json()
            assert data_upper["success"] is True
            assert len(data_upper["data"]["tools"]) >= 1

        except httpx.ConnectError:
            pytest.skip("Cannot connect to API server. Please ensure the server is running.")
        except Exception as e:
            pytest.fail(f"Unexpected error: {e}")
        finally:
            self.cleanup_test_tools()

    def test_search_tools_by_name_only(self):
        """Test searching only in name field."""
        self.create_test_tool("user_query", "Get products from database", "SELECT * FROM users")

        try:
            response = self.client.get(
                f"{self.base_url}/dmcp/tools/search",
                params={"q": "user", "fields": "name"},
                headers=self.headers,
            )

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True

            search_result = data["data"]
            assert len(search_result["tools"]) >= 1
            assert any("user" in tool["name"].lower() for tool in search_result["tools"])

            response_no_match = self.client.get(
                f"{self.base_url}/dmcp/tools/search",
                params={"q": "products", "fields": "name"},
                headers=self.headers,
            )

            assert response_no_match.status_code == 200
            data_no_match = response_no_match.json()
            assert data_no_match["success"] is True

        except httpx.ConnectError:
            pytest.skip("Cannot connect to API server. Please ensure the server is running.")
        except Exception as e:
            pytest.fail(f"Unexpected error: {e}")
        finally:
            self.cleanup_test_tools()

    def test_search_tools_by_description_only(self):
        """Test searching only in description field."""
        self.create_test_tool("query1", "Get all users from database", "SELECT * FROM users")

        try:
            response = self.client.get(
                f"{self.base_url}/dmcp/tools/search",
                params={"q": "users", "fields": "description"},
                headers=self.headers,
            )

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True

            search_result = data["data"]
            assert len(search_result["tools"]) >= 1
            assert any("users" in tool["description"].lower() for tool in search_result["tools"])

        except httpx.ConnectError:
            pytest.skip("Cannot connect to API server. Please ensure the server is running.")
        except Exception as e:
            pytest.fail(f"Unexpected error: {e}")
        finally:
            self.cleanup_test_tools()

    def test_search_tools_pagination(self):
        """Test pagination in search results."""
        for i in range(5):
            self.create_test_tool(f"test_tool_{i}", f"Test tool number {i}", "SELECT 1")

        try:
            response_page1 = self.client.get(
                f"{self.base_url}/dmcp/tools/search",
                params={"q": "test", "limit": 2, "offset": 0},
                headers=self.headers,
            )

            assert response_page1.status_code == 200
            data_page1 = response_page1.json()
            assert data_page1["success"] is True

            result_page1 = data_page1["data"]
            assert len(result_page1["tools"]) <= 2
            assert result_page1["limit"] == 2
            assert result_page1["offset"] == 0

            response_page2 = self.client.get(
                f"{self.base_url}/dmcp/tools/search",
                params={"q": "test", "limit": 2, "offset": 2},
                headers=self.headers,
            )

            assert response_page2.status_code == 200
            data_page2 = response_page2.json()
            assert data_page2["success"] is True

            result_page2 = data_page2["data"]
            assert result_page2["offset"] == 2

        except httpx.ConnectError:
            pytest.skip("Cannot connect to API server. Please ensure the server is running.")
        except Exception as e:
            pytest.fail(f"Unexpected error: {e}")
        finally:
            self.cleanup_test_tools()

    def test_search_tools_empty_query(self):
        """Test search with empty query should fail."""
        try:
            response = self.client.get(
                f"{self.base_url}/dmcp/tools/search",
                params={"q": ""},
                headers=self.headers,
            )

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is False
            assert len(data["errors"]) > 0

        except httpx.ConnectError:
            pytest.skip("Cannot connect to API server. Please ensure the server is running.")
        except Exception as e:
            pytest.fail(f"Unexpected error: {e}")

    def test_search_tools_invalid_limit(self):
        """Test search with invalid limit."""
        try:
            response = self.client.get(
                f"{self.base_url}/dmcp/tools/search",
                params={"q": "test", "limit": 200},
                headers=self.headers,
            )

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is False
            assert len(data["errors"]) > 0

        except httpx.ConnectError:
            pytest.skip("Cannot connect to API server. Please ensure the server is running.")
        except Exception as e:
            pytest.fail(f"Unexpected error: {e}")

    def test_search_tools_invalid_offset(self):
        """Test search with invalid offset."""
        try:
            response = self.client.get(
                f"{self.base_url}/dmcp/tools/search",
                params={"q": "test", "offset": -1},
                headers=self.headers,
            )

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is False
            assert len(data["errors"]) > 0

        except httpx.ConnectError:
            pytest.skip("Cannot connect to API server. Please ensure the server is running.")
        except Exception as e:
            pytest.fail(f"Unexpected error: {e}")

    def test_search_tools_without_auth(self):
        """Test search without authentication should fail."""
        try:
            response = self.client.get(
                f"{self.base_url}/dmcp/tools/search",
                params={"q": "test"},
            )

            assert response.status_code == 401

        except httpx.ConnectError:
            pytest.skip("Cannot connect to API server. Please ensure the server is running.")
        except Exception as e:
            pytest.fail(f"Unexpected error: {e}")

    def test_search_tools_wildcard_escaping(self):
        """Test that special SQL characters are properly escaped."""
        self.create_test_tool("test_100%_complete", "A tool with percent sign", "SELECT 1")
        self.create_test_tool("test_user_data", "A tool with underscore", "SELECT 1")

        try:
            response = self.client.get(
                f"{self.base_url}/dmcp/tools/search",
                params={"q": "100%"},
                headers=self.headers,
            )

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True

            search_result = data["data"]
            matching_tools = [tool for tool in search_result["tools"] if "100%" in tool["name"]]
            assert len(matching_tools) >= 1

        except httpx.ConnectError:
            pytest.skip("Cannot connect to API server. Please ensure the server is running.")
        except Exception as e:
            pytest.fail(f"Unexpected error: {e}")
        finally:
            self.cleanup_test_tools()

    def test_search_tools_no_results(self):
        """Test search with no matching results."""
        self.create_test_tool("user_query", "Get users", "SELECT * FROM users")

        try:
            response = self.client.get(
                f"{self.base_url}/dmcp/tools/search",
                params={"q": "nonexistent_xyz_123"},
                headers=self.headers,
            )

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True

            search_result = data["data"]
            assert len(search_result["tools"]) == 0
            assert search_result["total_count"] == 0
            assert search_result["has_more"] is False

        except httpx.ConnectError:
            pytest.skip("Cannot connect to API server. Please ensure the server is running.")
        except Exception as e:
            pytest.fail(f"Unexpected error: {e}")
        finally:
            self.cleanup_test_tools()

    def test_search_tools_has_more_flag(self):
        """Test has_more flag in pagination."""
        for i in range(10):
            self.create_test_tool(f"search_test_{i}", f"Test tool {i}", "SELECT 1")

        try:
            response = self.client.get(
                f"{self.base_url}/dmcp/tools/search",
                params={"q": "search_test", "limit": 5, "offset": 0},
                headers=self.headers,
            )

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True

            search_result = data["data"]
            if search_result["total_count"] > 5:
                assert search_result["has_more"] is True

            response_last = self.client.get(
                f"{self.base_url}/dmcp/tools/search",
                params={"q": "search_test", "limit": 5, "offset": search_result["total_count"]},
                headers=self.headers,
            )

            assert response_last.status_code == 200
            data_last = response_last.json()
            assert data_last["success"] is True
            assert data_last["data"]["has_more"] is False

        except httpx.ConnectError:
            pytest.skip("Cannot connect to API server. Please ensure the server is running.")
        except Exception as e:
            pytest.fail(f"Unexpected error: {e}")
        finally:
            self.cleanup_test_tools()
