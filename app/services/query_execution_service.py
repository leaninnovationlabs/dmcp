from typing import Optional, Dict, Any
import time
import re
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
from .jinja_template_service import JinjaTemplateService


class QueryExecutionService:
    """Service for query execution operations."""
    
    def __init__(self, db: AsyncSession):
        self.query_repository = QueryRepository(db)
        self.datasource_repository = DatasourceRepository(db)
        self.connection_manager = DatabaseConnectionManager()
        self.template_service = JinjaTemplateService()
    
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
            # Pre-process SQL with Jinja templates if needed
            processed_sql = self._preprocess_sql_template(sql, parameters)
            
            # Get connection to the target database
            connection = await self.connection_manager.get_connection(datasource)
            
            # Apply pagination if requested
            if pagination:
                processed_sql = self._apply_pagination(processed_sql, pagination)

            # print(f"Executing query: {processed_sql}")
            # print(f"Parameters: {parameters}")
            
            # Execute the query
            result = await connection.execute(processed_sql, parameters)
            
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
                # Get total count for pagination - use processed SQL without LIMIT
                original_processed_sql = processed_sql
                if "LIMIT" in processed_sql.upper():
                    # Remove LIMIT clause for count query
                    limit_index = processed_sql.upper().find("LIMIT")
                    original_processed_sql = processed_sql[:limit_index].strip()
                
                count_sql = f"SELECT COUNT(*) as total FROM ({original_processed_sql}) as count_query"
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
    
    def _preprocess_sql_template(self, sql: str, parameters: Dict[str, Any]) -> str:
        """
        Pre-process SQL with Jinja templates if template syntax is detected.
        
        Args:
            sql: The SQL query string
            parameters: Parameters for template substitution
            
        Returns:
            Processed SQL string
        """
        # Check if the SQL contains Jinja template syntax
        if self._contains_jinja_syntax(sql):
            try:
                # Validate template variables
                missing_vars = self.template_service.validate_template_variables(sql, parameters)
                if missing_vars:
                    missing_var_names = list(missing_vars.keys())
                    raise QueryExecutionError(
                        None, 
                        f"Missing required template variables: {', '.join(missing_var_names)}"
                    )
                
                # Render the template
                return self.template_service.render_template(sql, parameters)
                
            except Exception as e:
                if isinstance(e, QueryExecutionError):
                    raise
                raise QueryExecutionError(None, f"Template processing failed: {str(e)}")
        
        # If no template syntax, return the original SQL
        return sql
    
    def _contains_jinja_syntax(self, sql: str) -> bool:
        """Check if SQL contains Jinja template syntax."""
        jinja_patterns = [
            r'{{\s*[^}]+}}',  # {{ variable }}
            r'{%\s*[^%]+%}',  # {% control structures %}
            r'{#\s*[^#]+#}',  # {# comments #}
        ]
        
        for pattern in jinja_patterns:
            if re.search(pattern, sql):
                return True
        
        return False 