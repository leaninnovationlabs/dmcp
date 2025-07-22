import traceback
from typing import Optional, Dict, Any
import time
import re
from sqlalchemy.ext.asyncio import AsyncSession

from ..repositories.tool_repository import ToolRepository
from ..repositories.datasource_repository import DatasourceRepository
from ..models.schemas import (
    PaginationRequest,
    PaginationResponse,
    ToolExecutionResponse,
)
from ..core.exceptions import (
    ToolNotFoundError,
    DatasourceNotFoundError,
    ToolExecutionError,
    DatabaseConnectionError,
)
from ..database_connections import DatabaseConnectionManager
from .jinja_template_service import JinjaTemplateService


class ToolExecutionService:
    """Service for tool execution operations."""
    
    def __init__(self, db: AsyncSession):
        self.tool_repository = ToolRepository(db)
        self.datasource_repository = DatasourceRepository(db)
        self.connection_manager = DatabaseConnectionManager()
        self.template_service = JinjaTemplateService()
    
    async def execute_named_tool(
        self,
        tool_id: int,
        parameters: Optional[Dict[str, Any]] = None,
        pagination: Optional[PaginationRequest] = None,
    ) -> ToolExecutionResponse:
        """Execute a named tool with parameters and pagination."""
        try:
            # Get the tool with its datasource
            tool = await self.tool_repository.get_with_datasource(tool_id)
            if not tool:
                raise ToolNotFoundError(tool_id)
            
            # Get the datasource
            datasource = await self.datasource_repository.get_by_id(tool.datasource_id)
            if not datasource:
                raise DatasourceNotFoundError(tool.datasource_id)
            
            print('++++++xxx')
            print(tool.sql)
            print(parameters)
            print('++++++xxx')

            return await self._execute_query(
                datasource, tool.sql, parameters or {}, pagination
            )
        except (ToolNotFoundError, DatasourceNotFoundError):
            raise
        except Exception as e:
            print(e)
            raise ToolExecutionError(tool_id, str(e))
    
    async def execute_raw_query(
        self,
        datasource_id: int,
        sql: str,
        parameters: Optional[Dict[str, Any]] = None,
        pagination: Optional[PaginationRequest] = None,
    ) -> ToolExecutionResponse:
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
            raise ToolExecutionError(None, str(e))
    
    async def _execute_query(
        self,
        datasource,
        sql: str,
        parameters: Dict[str, Any],
        pagination: Optional[PaginationRequest] = None,
    ) -> ToolExecutionResponse:
        """Execute a query with parameters and pagination."""
        start_time = time.time()
        
        try:
            print('++++++')
            print(sql)
            print(parameters)
            # Process SQL with Jinja templates if needed
            processed_sql = self.template_service.process_sql_template(sql, parameters)

            print('processed_sql', processed_sql)
            print('parameters', parameters)
            
            # Get database connection
            connection = await self.connection_manager.get_connection(datasource)
            
            # Execute query with pagination
            if pagination:
                # Add pagination to the query
                offset = (pagination.page - 1) * pagination.page_size
                limit = pagination.page_size
                
                processed_sql_with_pagination = processed_sql

                # For PostgreSQL and MySQL, we can use LIMIT/OFFSET
                if datasource.database_type in ['postgresql', 'mysql']:
                    processed_sql_with_pagination += f" LIMIT {limit} OFFSET {offset}"
                
                print('processed_sql_with_pagination', processed_sql_with_pagination)

                # Execute the paginated query
                result_wrapper = await connection.execute(processed_sql_with_pagination)
                result_data = await result_wrapper.fetchall()
                
                # Get total count for pagination info
                count_sql = f"SELECT COUNT(*) as total FROM ({processed_sql}) as count_query"
                print(count_sql)

                count_result_wrapper = await connection.execute(count_sql)
                count_result_data = await count_result_wrapper.fetchall()
                total_items = count_result_data[0]['total'] if count_result_data else 0
                
                # Calculate pagination info
                total_pages = (total_items + pagination.page_size - 1) // pagination.page_size
                pagination_response = PaginationResponse(
                    page=pagination.page,
                    page_size=pagination.page_size,
                    total_pages=total_pages,
                    total_items=total_items,
                    has_next=pagination.page < total_pages,
                    has_prev=pagination.page > 1,
                )
            else:
                # Execute without pagination
                result_wrapper = await connection.execute(processed_sql)
                result_data = await result_wrapper.fetchall()
                pagination_response = None
            
            execution_time = (time.time() - start_time) * 1000  # Convert to milliseconds
            
            # result_data is now a list of dictionaries from all database connections
            data = result_data or []
            
            return ToolExecutionResponse(
                success=True,
                data=data,
                columns=list(data[0].keys()) if data else [],
                row_count=len(data),
                execution_time_ms=execution_time,
                pagination=pagination_response,
            )
            
        except Exception as e:
            print(e)
            print(traceback.format_exc())
            execution_time = (time.time() - start_time) * 1000
            return ToolExecutionResponse(
                success=False,
                data=[],
                columns=[],
                row_count=0,
                execution_time_ms=execution_time,
                pagination=None,
                error=str(e),
            )
    
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
                    raise ToolExecutionError(
                        None, 
                        f"Missing required template variables: {', '.join(missing_var_names)}"
                    )
                
                # Render the template
                return self.template_service.render_template(sql, parameters)
                
            except Exception as e:
                if isinstance(e, ToolExecutionError):
                    raise
                raise ToolExecutionError(None, f"Template processing failed: {str(e)}")
        
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