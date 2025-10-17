#!/usr/bin/env python3
"""
Test Databricks datasource functionality.
"""

from app.models.schemas import DatabaseType


class TestDatabricksDatasource:
    """Test Databricks datasource operations."""

    def test_create_databricks_datasource(
        self, api_base_url, http_client, auth_headers, databricks_config
    ):
        """Test creating a Databricks datasource."""
        response = http_client.post(
            f"{api_base_url}/datasources", headers=auth_headers, json=databricks_config
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["database_type"] == DatabaseType.DATABRICKS.value
        assert data["data"]["name"] == databricks_config["name"]
        assert data["data"]["host"] == databricks_config["host"]

        # Clean up - delete the created datasource
        datasource_id = data["data"]["id"]
        delete_response = http_client.delete(
            f"{api_base_url}/datasources/{datasource_id}", headers=auth_headers
        )
        assert delete_response.status_code == 200

    def test_list_datasources_includes_databricks(
        self, api_base_url, http_client, auth_headers, databricks_config
    ):
        """Test that Databricks datasources are included in the list."""
        # First create a Databricks datasource
        create_response = http_client.post(
            f"{api_base_url}/datasources", headers=auth_headers, json=databricks_config
        )
        assert create_response.status_code == 200
        datasource_id = create_response.json()["data"]["id"]

        try:
            # List all datasources
            list_response = http_client.get(
                f"{api_base_url}/datasources", headers=auth_headers
            )

            assert list_response.status_code == 200
            data = list_response.json()
            assert data["success"] is True

            # Check if our Databricks datasource is in the list
            datasources = data["data"]
            databricks_datasources = [
                ds
                for ds in datasources
                if ds["database_type"] == DatabaseType.DATABRICKS.value
            ]
            assert len(databricks_datasources) > 0

            # Check that our specific datasource is there
            our_datasource = next(
                (ds for ds in datasources if ds["id"] == datasource_id), None
            )
            assert our_datasource is not None
            assert our_datasource["database_type"] == DatabaseType.DATABRICKS.value

        finally:
            # Clean up
            http_client.delete(
                f"{api_base_url}/datasources/{datasource_id}", headers=auth_headers
            )

    def test_databricks_connection_registry(self):
        """Test that Databricks connection is properly registered."""
        from app.datasources import CONNECTION_REGISTRY
        from app.datasources.databricks import DatabricksConnection

        assert "databricks" in CONNECTION_REGISTRY
        assert CONNECTION_REGISTRY["databricks"] == DatabricksConnection

    def test_databricks_connection_class_exists(self):
        """Test that DatabricksConnection class exists and has required methods."""
        from app.datasources.databricks import DatabricksConnection

        # Check that the class exists
        assert DatabricksConnection is not None

        # Check that it has the required abstract methods
        assert hasattr(DatabricksConnection, "_execute_query")
        assert hasattr(DatabricksConnection, "_convert_parameters")
        assert hasattr(DatabricksConnection, "close")
        assert hasattr(DatabricksConnection, "create")
