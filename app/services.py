import time
from typing import Any, Dict, List, Optional

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from .database_connections import DatabaseConnectionManager
from .models.database import Datasource, Tool
from .models.schemas import (
    DatasourceCreate,
    DatasourceResponse,
    PaginationRequest,
    PaginationResponse,
    ToolCreate,
    ToolResponse,
)


class DatasourceService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_datasource(
        self, datasource: DatasourceCreate
    ) -> DatasourceResponse:
        """Create a new datasource."""
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

        # Set password using the property to trigger encryption
        db_datasource.decrypted_password = datasource.password

        self.db.add(db_datasource)
        await self.db.commit()
        await self.db.refresh(db_datasource)

        return DatasourceResponse.model_validate(db_datasource)

    async def list_datasources(self) -> List[DatasourceResponse]:
        """List all datasources."""
        result = await self.db.execute(select(Datasource))
        datasources = result.scalars().all()
        return [DatasourceResponse.model_validate(ds) for ds in datasources]

    async def get_datasource(self, datasource_id: int) -> Optional[DatasourceResponse]:
        """Get a specific datasource by ID."""
        result = await self.db.execute(
            select(Datasource).where(Datasource.id == datasource_id)
        )
        datasource = result.scalar_one_or_none()
        if datasource:
            return DatasourceResponse.model_validate(datasource)
        return None

    async def delete_datasource(self, datasource_id: int) -> bool:
        """Delete a datasource by ID."""
        result = await self.db.execute(
            delete(Datasource).where(Datasource.id == datasource_id)
        )
        await self.db.commit()
        return result.rowcount > 0


class ToolService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_tool(self, tool: ToolCreate) -> ToolResponse:
        """Create a new named tool."""
        # Verify datasource exists
        datasource_result = await self.db.execute(
            select(Datasource).where(Datasource.id == tool.datasource_id)
        )
        if not datasource_result.scalar_one_or_none():
            raise ValueError(f"Datasource with ID {tool.datasource_id} not found")

        db_tool = Tool(
            name=tool.name,
            description=tool.description,
            sql=tool.sql,
            datasource_id=tool.datasource_id,
            parameters=tool.parameters or [],
        )

        self.db.add(db_tool)
        await self.db.commit()
        await self.db.refresh(db_tool)

        return ToolResponse.model_validate(db_tool)

    async def list_tools(self) -> List[ToolResponse]:
        """List all named tools."""
        result = await self.db.execute(
            select(Tool).options(selectinload(Tool.datasource))
        )
        tools = result.scalars().all()
        return [ToolResponse.model_validate(t) for t in tools]

    async def get_tool(self, tool_id: int) -> Optional[ToolResponse]:
        """Get a specific named tool by ID."""
        result = await self.db.execute(
            select(Tool)
            .where(Tool.id == tool_id)
            .options(selectinload(Tool.datasource))
        )
        tool = result.scalar_one_or_none()
        if tool:
            return ToolResponse.model_validate(tool)
        return None

    async def delete_tool(self, tool_id: int) -> bool:
        """Delete a named tool by ID."""
        result = await self.db.execute(delete(Tool).where(Tool.id == tool_id))
        await self.db.commit()
        return result.rowcount > 0


class QueryExecutionService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.connection_manager = DatabaseConnectionManager()

    async def execute_named_query(
        self,
        query_id: int,
        parameters: Optional[Dict[str, Any]] = None,
        pagination: Optional[PaginationRequest] = None,
    ) -> QueryExecutionResponse:
        """Execute a named query with parameters and pagination."""
        # Get the query
        query_result = await self.db.execute(
            select(Query)
            .where(Query.id == query_id)
            .options(selectinload(Query.datasource))
        )
        query = query_result.scalar_one_or_none()

        if not query:
            raise ValueError(f"Query with ID {query_id} not found")

        # Get the datasource
        datasource_result = await self.db.execute(
            select(Datasource).where(Datasource.id == query.datasource_id)
        )
        datasource = datasource_result.scalar_one_or_none()

        if not datasource:
            raise ValueError(f"Datasource with ID {query.datasource_id} not found")

        return await self._execute_query(
            datasource, query.sql, parameters or {}, pagination
        )

    async def execute_raw_query(
        self,
        datasource_id: int,
        sql: str,
        parameters: Optional[Dict[str, Any]] = None,
        pagination: Optional[PaginationRequest] = None,
    ) -> QueryExecutionResponse:
        """Execute a raw SQL query with parameters and pagination."""
        # Get the datasource
        datasource_result = await self.db.execute(
            select(Datasource).where(Datasource.id == datasource_id)
        )
        datasource = datasource_result.scalar_one_or_none()

        if not datasource:
            raise ValueError(f"Datasource with ID {datasource_id} not found")

        return await self._execute_query(datasource, sql, parameters or {}, pagination)

    async def _execute_query(
        self,
        datasource: Datasource,
        sql: str,
        parameters: Dict[str, Any],
        pagination: Optional[PaginationRequest] = None,
    ) -> QueryExecutionResponse:
        """Execute a query against a datasource."""
        start_time = time.time()

        try:
            # Get connection to the target database
            connection = await self.connection_manager.get_connection(datasource)

            # Apply pagination if requested
            if pagination:
                sql = self._apply_pagination(sql, pagination)

            # Execute the query
            result = await connection.execute(sql, parameters)

            # Process results
            data = []
            columns = []

            if result.returns_rows:
                # Get column names
                if hasattr(result, "keys"):
                    columns = list(result.keys())
                elif hasattr(result, "column_names"):
                    columns = result.column_names

                # Fetch all rows
                rows = await result.fetchall()
                data = [dict(zip(columns, row)) for row in rows]

            execution_time = (
                time.time() - start_time
            ) * 1000  # Convert to milliseconds

            # Calculate pagination info
            pagination_response = None
            if pagination:
                # Get total count for pagination
                count_sql = f"SELECT COUNT(*) as total FROM ({sql.split('LIMIT')[0]}) as count_query"
                count_result = await connection.execute(count_sql, parameters)
                total_items = (await count_result.fetchone())[0]

                pagination_response = PaginationResponse(
                    page=pagination.page,
                    page_size=pagination.page_size,
                    total_items=total_items,
                    total_pages=(total_items + pagination.page_size - 1)
                    // pagination.page_size,
                    has_next=pagination.page * pagination.page_size < total_items,
                    has_previous=pagination.page > 1,
                )

            return QueryExecutionResponse(
                success=True,
                data=data,
                columns=columns,
                row_count=len(data),
                execution_time_ms=execution_time,
                pagination=pagination_response,
            )

        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            return QueryExecutionResponse(
                success=False,
                data=[],
                columns=[],
                row_count=0,
                execution_time_ms=execution_time,
                error=str(e),
            )

    def _apply_pagination(self, sql: str, pagination: PaginationRequest) -> str:
        """Apply pagination to SQL query."""
        offset = (pagination.page - 1) * pagination.page_size

        # Simple pagination - this might need to be database-specific
        if "LIMIT" not in sql.upper():
            sql += f" LIMIT {pagination.page_size} OFFSET {offset}"
        else:
            # If LIMIT already exists, we need to be more careful
            # This is a simplified approach
            sql = sql.replace("LIMIT", f"LIMIT {pagination.page_size} OFFSET {offset}")

        return sql
