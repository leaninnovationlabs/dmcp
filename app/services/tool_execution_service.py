import re
import time
import traceback
from typing import Any, Dict, Optional

import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.exceptions import DatasourceNotFoundError, ToolExecutionError, ToolNotFoundError
from ..database_connections import DatabaseConnectionManager
from ..models.schemas import PaginationRequest, PaginationResponse, ToolExecutionResponse
from ..repositories.datasource_repository import DatasourceRepository
from ..repositories.tool_repository import ToolRepository
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

            # Get the datasource (if provided)
            datasource = None
            if tool.datasource_id is not None:
                datasource = await self.datasource_repository.get_by_id(tool.datasource_id)
                if not datasource:
                    raise DatasourceNotFoundError(tool.datasource_id)

            # Route to appropriate execution method based on tool type
            if tool.type in ["code", "python"]:
                # Execute Python code
                if not tool.tool_code:
                    raise ToolExecutionError(tool_id, "Tool is of type 'code' but has no tool_code defined")
                return await self._execute_tool_code(datasource, tool.tool_code, parameters or {}, pagination)
            else:
                # Execute SQL (default for "query" type)
                if not tool.sql:
                    raise ToolExecutionError(tool_id, "Tool is of type 'query' but has no sql defined")
                if not datasource:
                    raise ToolExecutionError(tool_id, "SQL/HTTP tools require a datasource")
                return await self._execute_query(datasource, tool.sql, parameters or {}, pagination)
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

            return await self._execute_query(datasource, sql, parameters or {}, pagination)
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
            # Process SQL with Jinja templates if needed
            processed_sql = self.template_service.process_sql_template(sql, parameters)

            # Get database connection
            connection = await self.connection_manager.get_connection(datasource)

            # Execute query with pagination
            if pagination:
                # Add pagination to the query
                offset = (pagination.page - 1) * pagination.page_size
                limit = pagination.page_size

                processed_sql_with_pagination = processed_sql

                # For PostgreSQL and MySQL, we can use LIMIT/OFFSET
                if datasource.database_type in ["postgresql", "mysql"]:
                    processed_sql_with_pagination += f" LIMIT {limit} OFFSET {offset}"

                print("processed_sql_with_pagination", processed_sql_with_pagination)

                # Execute the paginated query
                result_wrapper = await connection.execute(processed_sql_with_pagination)
                result_data = await result_wrapper.fetchall()

                # Get total count for pagination info
                count_sql = f"SELECT COUNT(*) as total FROM ({processed_sql}) as count_query"
                print(count_sql)

                count_result_wrapper = await connection.execute(count_sql)
                count_result_data = await count_result_wrapper.fetchall()
                total_items = count_result_data[0]["total"] if count_result_data else 0

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
                        f"Missing required template variables: {', '.join(missing_var_names)}",
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
            r"{{\s*[^}]+}}",  # {{ variable }}
            r"{%\s*[^%]+%}",  # {% control structures %}
            r"{#\s*[^#]+#}",  # {# comments #}
        ]

        for pattern in jinja_patterns:
            if re.search(pattern, sql):
                return True

        return False

    async def _execute_tool_code(
        self,
        datasource,
        code: str,
        parameters: Dict[str, Any],
        pagination: Optional[PaginationRequest] = None,
    ) -> ToolExecutionResponse:
        """Execute Python code with restricted execution environment."""
        start_time = time.time()

        try:
            # Create helper function for executing SQL
            async def execute_sql(datasource_name: str, sql: str, params: Optional[Dict[str, Any]] = None):
                """Helper function to execute SQL against a datasource by name."""
                # Look up datasource by name
                ds = await self.datasource_repository.get_by_name(datasource_name)
                if not ds:
                    raise DatasourceNotFoundError(f"Datasource '{datasource_name}' not found")

                # Process SQL with Jinja templates if needed
                processed_sql = self.template_service.process_sql_template(sql, params or {})

                # Get database connection
                connection = await self.connection_manager.get_connection(ds)

                # Execute query
                result_wrapper = await connection.execute(processed_sql)
                result_data = await result_wrapper.fetchall()

                # Convert result data to list of dictionaries
                return [dict(row) for row in result_data]

            # Create helper function for HTTP requests
            async def http_request(
                url: str,
                method: str = "GET",
                headers: Optional[Dict[str, str]] = None,
                data: Optional[Any] = None,
            ):
                """Helper function to make HTTP requests."""
                async with httpx.AsyncClient(timeout=30.0) as client:
                    if method.upper() == "GET":
                        response = await client.get(url, headers=headers)
                    elif method.upper() == "POST":
                        response = await client.post(url, headers=headers, json=data)
                    elif method.upper() == "PUT":
                        response = await client.put(url, headers=headers, json=data)
                    elif method.upper() == "DELETE":
                        response = await client.delete(url, headers=headers)
                    else:
                        raise ValueError(f"Unsupported HTTP method: {method}")

                    response.raise_for_status()

                    # Try to parse as JSON, otherwise return text
                    try:
                        return response.json()
                    except Exception:
                        return response.text

            # Define safe built-ins
            safe_builtins = {
                "len": len,
                "str": str,
                "int": int,
                "float": float,
                "dict": dict,
                "list": list,
                "bool": bool,
                "range": range,
                "enumerate": enumerate,
                "zip": zip,
                "sum": sum,
                "min": min,
                "max": max,
                "abs": abs,
                "round": round,
                "sorted": sorted,
                "print": print,  # Allow print for debugging
            }

            # Create restricted globals
            restricted_globals = {
                "__builtins__": safe_builtins,
                "datasource": datasource.name,  # Pass datasource name as string
                "execute_sql": execute_sql,
                "http_request": http_request,
                "params": parameters,
            }

            # Create locals dictionary to capture result
            restricted_locals = {}

            # Wrap the code in an async function to support await
            async_code = f"""
async def __user_code__():
{chr(10).join("    " + line for line in code.split(chr(10)))}
    return result
"""

            # Execute the code to define the function (sync)
            exec(async_code, restricted_globals, restricted_locals)

            # Now await the async function (async)
            result_data = await restricted_locals["__user_code__"]()

            # Validate result is a list of dictionaries
            if not isinstance(result_data, list):
                raise ToolExecutionError(
                    None,
                    f"Result must be a list of dictionaries, got {type(result_data).__name__}. "
                    f"If you're calling execute_sql() or http_request(), make sure to use 'await'.",
                )

            # Validate all items in the list are dictionaries
            if result_data and not all(isinstance(item, dict) for item in result_data):
                non_dict_types = set(type(item).__name__ for item in result_data if not isinstance(item, dict))
                raise ToolExecutionError(
                    None, f"Result must be a list of dictionaries, but found items of type: {', '.join(non_dict_types)}"
                )

            execution_time = (time.time() - start_time) * 1000  # Convert to milliseconds

            # Apply pagination if requested
            if pagination:
                total_items = len(result_data)
                start_idx = (pagination.page - 1) * pagination.page_size
                end_idx = start_idx + pagination.page_size
                paginated_data = result_data[start_idx:end_idx]

                total_pages = (total_items + pagination.page_size - 1) // pagination.page_size
                pagination_response = PaginationResponse(
                    page=pagination.page,
                    page_size=pagination.page_size,
                    total_pages=total_pages,
                    total_items=total_items,
                    has_next=pagination.page < total_pages,
                    has_prev=pagination.page > 1,
                )
                data = paginated_data
            else:
                data = result_data
                pagination_response = None

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
