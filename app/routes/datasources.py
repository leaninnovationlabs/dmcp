import json

from app.core.token_processor import get_payload
from app.core.responses import api_response
from app.core.exceptions import AuthenticationError
from app.services.datasource_service import DatasourceService
from app.database import get_db

class DatasourcesRouter:
    def __init__(self, mcp):
        self.mcp = mcp

    def register_routes(self):
        @self.mcp.custom_route("/datasources/field-config", methods=["GET"])
        async def get_datasource_field_config(request):
            """Get field configuration for all datasource types."""
            field_configs = {
                "sqlite": {
                    "database_type": "sqlite",
                    "fields": [
                        {
                            "name": "sqlite_database",
                            "type": "text",
                            "label": "Database File Path",
                            "required": True,
                            "placeholder": "/path/to/database.db",
                            "description": "Path to the SQLite database file"
                        }
                    ],
                    "sections": [
                        {
                            "id": "sqlite-config",
                            "title": "SQLite Configuration",
                            "description": "Configure your SQLite database connection"
                        }
                    ]
                },
                "postgresql": {
                    "database_type": "postgresql",
                    "fields": [
                        {
                            "name": "host",
                            "type": "text",
                            "label": "Host",
                            "required": True,
                            "placeholder": "localhost"
                        },
                        {
                            "name": "port",
                            "type": "number",
                            "label": "Port",
                            "required": True,
                            "placeholder": "5432"
                        },
                        {
                            "name": "database",
                            "type": "text",
                            "label": "Database Name",
                            "required": True,
                            "placeholder": "mydatabase"
                        },
                        {
                            "name": "username",
                            "type": "text",
                            "label": "Username",
                            "required": True,
                            "placeholder": "myuser"
                        },
                        {
                            "name": "password",
                            "type": "password",
                            "label": "Password",
                            "required": True,
                            "placeholder": "mypassword"
                        }
                    ],
                    "sections": [
                        {
                            "id": "postgresql-config",
                            "title": "PostgreSQL Configuration",
                            "description": "Configure your PostgreSQL database connection"
                        }
                    ]
                }
            }
            return api_response(field_configs)


        @self.mcp.custom_route("/datasources", methods=["POST"])
        async def create_datasource(request):

            """Create a new datasource."""
            try:
                payload = await get_payload(request.headers.get("authorization"))
                body = await request.body()
                data = json.loads(body) if body else {}
                
                # Transform frontend format to backend format
                transformed_data = {
                    "name": data.get("name"),
                    "database_type": data.get("database_type"),
                    "database": data.get("database", "default"),  # Default database name
                    "additional_params": data.get("connection_params", {})
                }
                
                # Extract specific fields from connection_params
                if "connection_params" in data:
                    params = data["connection_params"]
                    if "host" in params:
                        transformed_data["host"] = params["host"]
                    if "port" in params:
                        transformed_data["port"] = params["port"]
                    if "database" in params:
                        transformed_data["database"] = params["database"]
                    if "username" in params:
                        transformed_data["username"] = params["username"]
                    if "password" in params:
                        transformed_data["password"] = params["password"]
                    if "sqlite_database" in params:
                        transformed_data["database"] = params["sqlite_database"]
                
                async for db in get_db():
                    service = DatasourceService(db)
                    from app.models.schemas import DatasourceCreate
                    datasource_data = DatasourceCreate(**transformed_data)
                    result = await service.create_datasource(datasource_data)
                    return api_response(result.model_dump())
            except Exception as e:
                return api_response(None, False, [f"Failed to create datasource: {str(e)}"])


        @self.mcp.custom_route("/datasources", methods=["GET"])
        async def list_datasources(request):
            """List all datasources."""

            try:
                payload = await get_payload(request.headers.get("authorization"))
                async for db in get_db():
                    service = DatasourceService(db)
                    result = await service.list_datasources()
                    return api_response([ds.model_dump() for ds in result])
            except AuthenticationError as e:
                return api_response(None, False, [f"Authentication failed: {e.message}"])
            except Exception as e:
                return api_response(None, False, [f"Failed to list datasources: {str(e)}"])


        @self.mcp.custom_route("/datasources/{datasource_id}", methods=["GET"])
        async def get_datasource(request):
            """Get specific datasource."""
            datasource_id = int(request.path_params.get("datasource_id"))
            
            async for db in get_db():
                service = DatasourceService(db)
                datasource = await service.get_datasource(datasource_id)
                if not datasource:
                    return api_response(None, False, ["Datasource not found"])
                return api_response(datasource.model_dump())




# @router.delete("/{datasource_id}", response_model=StandardAPIResponse)
# async def delete_datasource(
#     datasource_id: int,
#     db: AsyncSession = Depends(get_db),
# ):
#     """Delete a datasource by ID."""
#     try:
#         service = DatasourceService(db)
#         success = await service.delete_datasource(datasource_id)
#         if not success:
#             raise_http_error(404, "Datasource not found")
#         return create_success_response(data={"message": "Datasource deleted successfully"})
#     except HTTPException:
#         raise
#     except ValueError as e:
#         raise_http_error(400, "Invalid datasource data", [str(e)])
#     except Exception as e:
#         raise_http_error(500, "Internal server error", [str(e)])


# @router.post("/{datasource_id}/test", response_model=StandardAPIResponse)
# async def test_datasource_connection(
#     datasource_id: int,
#     db: AsyncSession = Depends(get_db),
# ):
#     """Test the database connection for a specific datasource."""
#     try:
#         service = DatasourceService(db)
#         result = await service.test_connection(datasource_id)
#         print(result)
#         if not result["success"]:
#             raise_http_error(400, "Connection test failed", [result["message"]])
#         return create_success_response(data=result)
#     except HTTPException:
#         raise
#     except Exception as e:
#         raise_http_error(500, "Internal server error", [str(e)]) 