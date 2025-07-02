from typing import Optional, Dict, Any
import time
from sqlalchemy.ext.asyncio import AsyncSession

from ..repositories.query_repository import QueryRepository
from ..repositories.datasource_repository import DatasourceRepository
from ..models.schemas import (
    PaginationRequest,
    PaginationResponse,
    QueryExecutionResponse,
)
from ..core.exceptions import (
    QueryNotFoundError,
    DatasourceNotFoundError,
    QueryExecutionError,
    DatabaseConnectionError,
)
from ..database_connections import DatabaseConnectionManager


class QueryExecutionService:
    """Service for query execution operations."""
    
    def __init__(self, db: AsyncSession):
        self.query_repository = QueryRepository(db)
        self.datasource_repository = DatasourceRepository(db)
        self.connection_manager = DatabaseConnectionManager()
    
    async def execute_named_query(
        self,
        query_id: int,
        parameters: Optional[Dict[str, Any]] = None,
        pagination: Optional[PaginationRequest] = None,
    ) -> QueryExecutionResponse:
        """Execute a named query with parameters and pagination."""
        try:
            # Get the query with its datasource
            query = await self.query_repository.get_with_datasource(query_id)
            if not query:
                raise QueryNotFoundError(query_id)
            
            # Get the datasource
            datasource = await self.datasource_repository.get_by_id(query.datasource_id)
            if not datasource:
                raise DatasourceNotFoundError(query.datasource_id)
            
            return await self._execute_query(
                datasource, query.sql, parameters or {}, pagination
            )
        except (QueryNotFoundError, DatasourceNotFoundError):
            raise
        except Exception as e:
            raise QueryExecutionError(query_id, str(e))
    
    async def execute_raw_query(
        self,
        datasource_id: int,
        sql: str,
        parameters: Optional[Dict[str, Any]] = None,
        pagination: Optional[PaginationRequest] = None,
    ) -> QueryExecutionResponse:
        """Execute a raw SQL query with parameters and pagination."""
        try:
            # Get the datasource
            datasource = await self.datasource_repository.get_by_id(datasource_id)
            if not datasource:
                raise DatasourceNotFoundError(datasource_id)
            
            return await self._execute_query(
                datasource, sql, parameters or {}, pagination
            )
        except DatasourceNotFoundError:
            raise
        except Exception as e:
            raise QueryExecutionError(None, str(e))
    
    async def _execute_query(
        self,
        datasource,
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

            print(f"Executing query: {sql}")
            print(f"Parameters: {parameters}")
            
            # Execute the query
            result = await connection.execute(sql, parameters)
            
            # Process results
            data = []
            columns = []
            
            if result.returns_rows:
                # Get column names
                if hasattr(result, 'keys'):
                    columns = result.keys
                elif hasattr(result, 'column_names'):
                    columns = result.column_names
                
                # Fetch all rows
                rows = await result.fetchall()
                data = [dict(zip(columns, row)) for row in rows]
            
            execution_time = (time.time() - start_time) * 1000  # Convert to milliseconds
            
            # Calculate pagination info
            pagination_response = None
            if pagination:
                # Get total count for pagination - use original SQL without LIMIT
                original_sql = sql
                if "LIMIT" in sql.upper():
                    # Remove LIMIT clause for count query
                    limit_index = sql.upper().find("LIMIT")
                    original_sql = sql[:limit_index].strip()
                
                count_sql = f"SELECT COUNT(*) as total FROM ({original_sql}) as count_query"
                count_result = await connection.execute(count_sql, parameters)
                count_row = await count_result.fetchone()
                total_items = count_row[0] if count_row else 0
                
                pagination_response = PaginationResponse(
                    page=pagination.page,
                    page_size=pagination.page_size,
                    total_items=total_items,
                    total_pages=(total_items + pagination.page_size - 1) // pagination.page_size,
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
            raise QueryExecutionError(None, str(e))
    
    def _apply_pagination(self, sql: str, pagination: PaginationRequest) -> str:
        """Apply pagination to SQL query."""
        offset = (pagination.page - 1) * pagination.page_size
        
        # Remove any existing LIMIT clause
        sql_upper = sql.upper()
        limit_index = sql_upper.find("LIMIT")
        if limit_index != -1:
            # Find the end of the LIMIT clause (end of line or semicolon)
            end_index = sql.find(";", limit_index)
            if end_index == -1:
                end_index = len(sql)
            sql = sql[:limit_index].strip()
        
        # Add new LIMIT clause
        sql += f" LIMIT {pagination.page_size} OFFSET {offset}"
        
        return sql 