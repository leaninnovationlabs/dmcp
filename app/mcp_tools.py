from typing import Dict, Any, List, Optional
from .services.datasource_service import DatasourceService
from .services.query_service import QueryService
from .services.query_execution_service import QueryExecutionService
from .models.schemas import (
    DatasourceCreate,
    QueryCreate,
    QueryExecutionRequest,
    RawQueryRequest,
    PaginationRequest,
)
from .database import get_db


class MCPTools:
    """MCP (Model Context Protocol) tools for database operations."""
    
    def __init__(self):
        pass
    
    async def create_datasource_tool(self, **kwargs) -> Dict[str, Any]:
        """Create a new datasource."""
        async for db in get_db():
            service = DatasourceService(db)
            datasource = DatasourceCreate(**kwargs)
            result = await service.create_datasource(datasource)
            return {
                "success": True,
                "datasource": result.model_dump(),
                "message": f"Datasource '{result.name}' created successfully"
            }
    
    async def list_datasources_tool(self) -> Dict[str, Any]:
        """List all datasources."""
        async for db in get_db():
            service = DatasourceService(db)
            datasources = await service.list_datasources()
            return {
                "success": True,
                "datasources": [ds.model_dump() for ds in datasources],
                "count": len(datasources)
            }
    
    async def create_query_tool(self, **kwargs) -> Dict[str, Any]:
        """Create a new named query."""
        async for db in get_db():
            service = QueryService(db)
            query = QueryCreate(**kwargs)
            result = await service.create_query(query)
            return {
                "success": True,
                "query": result.model_dump(),
                "message": f"Query '{result.name}' created successfully"
            }
    
    async def list_queries_tool(self) -> Dict[str, Any]:
        """List all named queries."""
        async for db in get_db():
            service = QueryService(db)
            queries = await service.list_queries()
            return {
                "success": True,
                "queries": [q.model_dump() for q in queries],
                "count": len(queries)
            }
    
    async def execute_query_tool(self, query_id: int, parameters: Optional[Dict[str, Any]] = None, 
                                page: int = 1, page_size: int = 10) -> Dict[str, Any]:
        """Execute a named query with parameters and pagination."""
        async for db in get_db():
            service = QueryExecutionService(db)
            pagination = PaginationRequest(page=page, page_size=page_size)
            result = await service.execute_named_query(query_id, parameters, pagination)
            return {
                "success": result.success,
                "data": result.data,
                "columns": result.columns,
                "row_count": result.row_count,
                "execution_time_ms": result.execution_time_ms,
                "pagination": result.pagination.model_dump() if result.pagination else None,
                "error": result.error
            }
    
    async def execute_raw_query_tool(self, datasource_id: int, sql: str, 
                                   parameters: Optional[Dict[str, Any]] = None,
                                   page: int = 1, page_size: int = 10) -> Dict[str, Any]:
        """Execute a raw SQL query with parameters and pagination."""
        async for db in get_db():
            service = QueryExecutionService(db)
            pagination = PaginationRequest(page=page, page_size=page_size)
            result = await service.execute_raw_query(datasource_id, sql, parameters, pagination)
            return {
                "success": result.success,
                "data": result.data,
                "columns": result.columns,
                "row_count": result.row_count,
                "execution_time_ms": result.execution_time_ms,
                "pagination": result.pagination.model_dump() if result.pagination else None,
                "error": result.error
            }


# MCP tool definitions
MCP_TOOLS = {
    "create_datasource": {
        "name": "create_datasource",
        "description": "Create a new database datasource with connection information",
        "parameters": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Name of the datasource"},
                "database_type": {"type": "string", "enum": ["postgresql", "mysql", "sqlite"], "description": "Type of database"},
                "host": {"type": "string", "description": "Database host"},
                "port": {"type": "integer", "description": "Database port"},
                "database": {"type": "string", "description": "Database name"},
                "username": {"type": "string", "description": "Database username"},
                "password": {"type": "string", "description": "Database password"},
                "connection_string": {"type": "string", "description": "Full connection string"},
                "ssl_mode": {"type": "string", "description": "SSL mode for connection"},
                "additional_params": {"type": "object", "description": "Additional connection parameters"}
            },
            "required": ["name", "database_type", "database"]
        }
    },
    "list_datasources": {
        "name": "list_datasources",
        "description": "List all available datasources",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    "create_query": {
        "name": "create_query",
        "description": "Create a new named query with parameter support",
        "parameters": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Name of the query"},
                "description": {"type": "string", "description": "Query description"},
                "sql": {"type": "string", "description": "SQL query with parameter placeholders"},
                "datasource_id": {"type": "integer", "description": "ID of the datasource to use"},
                "parameters": {"type": "array", "description": "Parameter definitions"}
            },
            "required": ["name", "sql", "datasource_id"]
        }
    },
    "list_queries": {
        "name": "list_queries",
        "description": "List all available named queries",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    "execute_query": {
        "name": "execute_query",
        "description": "Execute a named query with parameters and pagination",
        "parameters": {
            "type": "object",
            "properties": {
                "query_id": {"type": "integer", "description": "ID of the query to execute"},
                "parameters": {"type": "object", "description": "Query parameters"},
                "page": {"type": "integer", "default": 1, "description": "Page number (1-based)"},
                "page_size": {"type": "integer", "default": 10, "description": "Number of items per page"}
            },
            "required": ["query_id"]
        }
    },
    "execute_raw_query": {
        "name": "execute_raw_query",
        "description": "Execute a raw SQL query with parameters and pagination",
        "parameters": {
            "type": "object",
            "properties": {
                "datasource_id": {"type": "integer", "description": "ID of the datasource to use"},
                "sql": {"type": "string", "description": "Raw SQL query"},
                "parameters": {"type": "object", "description": "Query parameters"},
                "page": {"type": "integer", "default": 1, "description": "Page number (1-based)"},
                "page_size": {"type": "integer", "default": 10, "description": "Number of items per page"}
            },
            "required": ["datasource_id", "sql"]
        }
    }
} 