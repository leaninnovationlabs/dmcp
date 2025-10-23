import time
from typing import Any, Dict, List, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from ..core.exceptions import DatasourceNotFoundError
from ..database_connections import DatabaseConnectionManager
from ..models.schemas import DatasourceCreate, DatasourceResponse
from ..repositories.datasource_repository import DatasourceRepository


class DatasourceService:
    """Service for datasource operations."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repository = DatasourceRepository(db)

    async def create_datasource(self, datasource: DatasourceCreate) -> DatasourceResponse:
        """Create a new datasource."""
        try:
            # Create the datasource instance first to handle password encryption
            from ..models.database import Datasource

            db_datasource = Datasource(
                name=datasource.name,
                database_type=datasource.database_type.value,
                host=datasource.host,
                port=datasource.port,
                database=datasource.database,
                username=datasource.username,
                connection_string=datasource.connection_string,
                ssl_mode=datasource.ssl_mode,
                additional_params=datasource.additional_params or {},
            )
            # Set password using the property to trigger encryption (only if password is provided)
            if datasource.password:
                db_datasource.decrypted_password = datasource.password

            # Save to database
            self.db.add(db_datasource)
            await self.db.commit()
            await self.db.refresh(db_datasource)

            return DatasourceResponse(
                id=db_datasource.id,
                name=db_datasource.name,
                database_type=db_datasource.database_type,
                host=db_datasource.host,
                port=db_datasource.port,
                database=db_datasource.database,
                username=db_datasource.username,
                password=db_datasource.decrypted_password,
                connection_string=db_datasource.connection_string,
                ssl_mode=db_datasource.ssl_mode,
                additional_params=db_datasource.additional_params,
                created_at=db_datasource.created_at,
                updated_at=db_datasource.updated_at,
            )
        except ValueError as e:
            raise ValueError(str(e))
        except Exception as e:
            raise Exception(f"Failed to create datasource: {str(e)}")

    async def list_datasources(self) -> List[DatasourceResponse]:
        """List all datasources."""
        try:
            datasources = await self.repository.get_all()
            return [DatasourceResponse.model_validate(ds) for ds in datasources]
        except Exception as e:
            raise Exception(f"Failed to list datasources: {str(e)}")

    async def get_datasource(self, datasource_id: int) -> Optional[DatasourceResponse]:
        """Get a specific datasource by ID."""
        try:
            datasource = await self.repository.get_by_id(datasource_id)
            if datasource:
                # Create response without password for security
                return DatasourceResponse(
                    id=datasource.id,
                    name=datasource.name,
                    database_type=datasource.database_type,
                    host=datasource.host,
                    port=datasource.port,
                    database=datasource.database,
                    username=datasource.username,
                    connection_string=datasource.connection_string,
                    ssl_mode=datasource.ssl_mode,
                    additional_params=datasource.additional_params,
                    created_at=datasource.created_at,
                    updated_at=datasource.updated_at,
                )
            return None
        except Exception as e:
            raise Exception(f"Failed to get datasource: {str(e)}")

    async def update_datasource(self, datasource_id: int, **kwargs) -> DatasourceResponse:
        """Update a datasource."""
        try:
            # Handle password encryption if password is being updated
            if "password" in kwargs:
                password_value = kwargs.pop("password")
                # Get the existing datasource
                datasource = await self.repository.get_by_id(datasource_id)
                if not datasource:
                    raise DatasourceNotFoundError(datasource_id)

                # Only update password if it's not empty or None
                if password_value and password_value.strip():
                    datasource.decrypted_password = password_value

                # Update other fields
                for key, value in kwargs.items():
                    setattr(datasource, key, value)

                await self.db.commit()
                await self.db.refresh(datasource)
                return DatasourceResponse(
                    id=datasource.id,
                    name=datasource.name,
                    database_type=datasource.database_type,
                    host=datasource.host,
                    port=datasource.port,
                    database=datasource.database,
                    username=datasource.username,
                    connection_string=datasource.connection_string,
                    ssl_mode=datasource.ssl_mode,
                    additional_params=datasource.additional_params,
                    created_at=datasource.created_at,
                    updated_at=datasource.updated_at,
                )
            else:
                # No password update, use normal repository method
                updated_datasource = await self.repository.update_datasource(datasource_id, **kwargs)
                return DatasourceResponse.model_validate(updated_datasource)
        except DatasourceNotFoundError:
            raise
        except ValueError as e:
            raise ValueError(str(e))
        except Exception as e:
            raise Exception(f"Failed to update datasource: {str(e)}")

    async def delete_datasource(self, datasource_id: int) -> bool:
        """Delete a datasource by ID."""
        try:
            return await self.repository.delete_datasource(datasource_id)
        except DatasourceNotFoundError:
            raise
        except ValueError as e:
            raise ValueError(str(e))
        except Exception as e:
            raise Exception(f"Failed to delete datasource: {str(e)}")

    async def get_datasource_with_queries(self, datasource_id: int) -> Optional[DatasourceResponse]:
        """Get a datasource with its associated queries."""
        try:
            datasource = await self.repository.get_with_queries(datasource_id)
            if datasource:
                return DatasourceResponse.model_validate(datasource)
            return None
        except Exception as e:
            raise Exception(f"Failed to get datasource with queries: {str(e)}")

    async def test_connection(self, datasource_id: int) -> Dict[str, Any]:
        """Test the database connection for a specific datasource."""
        start_time = time.time()

        try:
            # Get the datasource
            datasource = await self.repository.get_by_id(datasource_id)
            if not datasource:
                raise DatasourceNotFoundError(datasource_id)

            # Test the connection
            connection_manager = DatabaseConnectionManager()
            connection = await connection_manager.get_connection(datasource)

            # Try to execute a simple query to test the connection
            if datasource.database_type == "sqlite":
                test_sql = "SELECT 1 as test"
            elif datasource.database_type == "postgresql":
                test_sql = "SELECT 1 as test"
            elif datasource.database_type == "mysql":
                test_sql = "SELECT 1 as test"
            else:
                test_sql = "SELECT 1 as test"

            result = await connection.execute(test_sql, {})
            test_row = await result.fetchone()

            connection_time = (time.time() - start_time) * 1000  # Convert to milliseconds

            if test_row and test_row["test"] == 1:
                return {
                    "success": True,
                    "message": f"Successfully connected to {datasource.database_type} database '{datasource.database}'",
                    "connection_time_ms": connection_time,
                    "error": None,
                }
            else:
                return {
                    "success": False,
                    "message": "Connection test failed - unexpected result",
                    "connection_time_ms": connection_time,
                    "error": "Test query did not return expected result",
                }

        except Exception as e:
            # Debug logging - removed print statement to avoid stdout pollution
            connection_time = (time.time() - start_time) * 1000
            return {
                "success": False,
                "message": "Failed to connect to database",
                "connection_time_ms": connection_time,
                "error": str(e),
            }

    async def test_connection_params(self, datasource: DatasourceCreate) -> Dict[str, Any]:
        """Test database connection with provided parameters without saving."""
        start_time = time.time()

        try:
            # Create a temporary datasource object for testing
            from ..models.database import Datasource

            temp_datasource = Datasource(
                name=datasource.name,
                database_type=datasource.database_type.value,
                host=datasource.host,
                port=datasource.port,
                database=datasource.database,
                username=datasource.username,
                connection_string=datasource.connection_string,
                ssl_mode=datasource.ssl_mode,
                additional_params=datasource.additional_params or {},
            )
            # Set password using the property to trigger encryption
            temp_datasource.decrypted_password = datasource.password

            # Test the connection
            connection_manager = DatabaseConnectionManager()
            connection = await connection_manager.get_connection(temp_datasource)

            # Try to execute a simple query to test the connection
            if datasource.database_type.value == "sqlite":
                test_sql = "SELECT 1 as test"
            elif datasource.database_type.value == "postgresql":
                test_sql = "SELECT 1 as test"
            elif datasource.database_type.value == "mysql":
                test_sql = "SELECT 1 as test"
            else:
                test_sql = "SELECT 1 as test"

            result = await connection.execute(test_sql, {})
            test_row = await result.fetchone()

            connection_time = (time.time() - start_time) * 1000  # Convert to milliseconds

            if test_row and test_row["test"] == 1:
                return {
                    "success": True,
                    "message": f"Successfully connected to {datasource.database_type.value} \
                        database '{datasource.database}'",
                    "connection_time_ms": connection_time,
                    "error": None,
                }
            else:
                return {
                    "success": False,
                    "message": "Connection test failed - unexpected result",
                    "connection_time_ms": connection_time,
                    "error": "Test query did not return expected result",
                }

        except Exception as e:
            connection_time = (time.time() - start_time) * 1000
            return {
                "success": False,
                "message": f"Failed to connect to database: {str(e)}",
                "connection_time_ms": connection_time,
                "error": str(e),
            }
