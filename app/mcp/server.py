# #!/usr/bin/env python3
# """
# MCP (Model Context Protocol) Server for DBMCP using FastMCP.

# This server exposes database operations as MCP tools that can be used
# by AI assistants and other MCP clients.
# """

import asyncio
import json
import logging
import sys
from typing import Any, Dict, List, Optional
from fastmcp import FastMCP
from pydantic import BaseModel, Field

from .tools import MCPTools
from ..database import init_db

from pathlib import Path
from dotenv import load_dotenv

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, stream=sys.stderr)
logger = logging.getLogger(__name__)


# Pydantic models for tool parameters
class CreateDatasourceParams(BaseModel):
    name: str = Field(..., description="Name of the datasource")
    database_type: str = Field(..., description="Type of database", enum=["postgresql", "mysql", "sqlite"])
    host: Optional[str] = Field(None, description="Database host")
    port: Optional[int] = Field(None, description="Database port")
    database: str = Field(..., description="Database name")
    username: Optional[str] = Field(None, description="Database username")
    password: Optional[str] = Field(None, description="Database password")
    connection_string: Optional[str] = Field(None, description="Full connection string")
    ssl_mode: Optional[str] = Field(None, description="SSL mode for connection")
    additional_params: Optional[Dict[str, Any]] = Field(None, description="Additional connection parameters")


class CreateQueryParams(BaseModel):
    name: str = Field(..., description="Name of the query")
    description: Optional[str] = Field(None, description="Query description")
    sql: str = Field(..., description="SQL query with parameter placeholders")
    datasource_id: int = Field(..., description="ID of the datasource to use")
    parameters: Optional[Dict[str, Any]] = Field(None, description="Parameter definitions as JSON object")


class ExecuteQueryParams(BaseModel):
    query_id: int = Field(..., description="ID of the query to execute")
    parameters: Optional[Dict[str, Any]] = Field(None, description="Query parameters")
    page: int = Field(1, description="Page number (1-based)")
    page_size: int = Field(10, description="Number of items per page")


class ExecuteRawQueryParams(BaseModel):
    datasource_id: int = Field(..., description="ID of the datasource to use")
    sql: str = Field(..., description="Raw SQL query")
    parameters: Optional[Dict[str, Any]] = Field(None, description="Query parameters")
    page: int = Field(1, description="Page number (1-based)")
    page_size: int = Field(10, description="Number of items per page")


class DBMCPToolsServer:
    """MCP Server that exposes database operations as tools using FastMCP."""
    
    def __init__(self):
        # self.mcp_tools = MCPTools()
        self.fastmcp = FastMCP("dbmcp")
        self._setup_tools()
    
    def _setup_tools(self):
        """Setup MCP tools using FastMCP decorators."""
        
        # @self.fastmcp.tool("create_datasource")
        # async def create_datasource(params: CreateDatasourceParams) -> str:
        #     """Create a new database datasource with connection information."""
        #     try:
        #         result = await self.mcp_tools.create_datasource_tool(**params.model_dump())
        #         return json.dumps(result, indent=2, default=str)
        #     except Exception as e:
        #         logger.error(f"Error creating datasource: {e}")
        #         return json.dumps({"success": False, "error": str(e)}, indent=2)
        
        # @self.fastmcp.tool("list_datasources")
        # async def list_datasources() -> str:
        #     """List all available datasources."""
        #     try:
        #         result = await self.mcp_tools.list_datasources_tool()
        #         return json.dumps(result, indent=2, default=str)
        #     except Exception as e:
        #         logger.error(f"Error listing datasources: {e}")
        #         return json.dumps({"success": False, "error": str(e)}, indent=2)
        
        # @self.fastmcp.tool("create_query")
        # async def create_query(params: CreateQueryParams) -> str:
        #     """Create a new named query with parameter support."""
        #     try:
        #         result = await self.mcp_tools.create_query_tool(**params.model_dump())
        #         return json.dumps(result, indent=2, default=str)
        #     except Exception as e:
        #         logger.error(f"Error creating query: {e}")
        #         return json.dumps({"success": False, "error": str(e)}, indent=2)
        
        # @self.fastmcp.tool("list_queries")
        # async def list_queries() -> str:
        #     """List all available named queries."""
        #     try:
        #         result = await self.mcp_tools.list_queries_tool()
        #         return json.dumps(result, indent=2, default=str)
        #     except Exception as e:
        #         logger.error(f"Error listing queries: {e}")
        #         return json.dumps({"success": False, "error": str(e)}, indent=2)
        

        # Dummy hello world tool
        @self.fastmcp.tool("hello_world")
        async def hello_world() -> str:
            """Return a simple hello world message."""
            return "Hello, world!"


        # @self.fastmcp.tool("execute_query")
        # async def execute_query(params: ExecuteQueryParams) -> str:
        #     """Execute a named query with parameters and pagination."""
        #     try:
        #         result = await self.mcp_tools.execute_query_tool(**params.model_dump())
        #         return json.dumps(result, indent=2, default=str)
        #     except Exception as e:
        #         logger.error(f"Error executing query: {e}")
        #         return json.dumps({"success": False, "error": str(e)}, indent=2)
        
        # @self.fastmcp.tool("execute_raw_query")
        # async def execute_raw_query(params: ExecuteRawQueryParams) -> str:
        #     """Execute a raw SQL query with parameters and pagination."""
        #     try:
        #         result = await self.mcp_tools.execute_raw_query_tool(**params.model_dump())
        #         return json.dumps(result, indent=2, default=str)
        #     except Exception as e:
        #         logger.error(f"Error executing raw query: {e}")
        #         return json.dumps({"success": False, "error": str(e)}, indent=2)
    
    def run(self):
        """Run the MCP server."""
        try:
            # Initialize database (synchronously)
            # import asyncio
            # asyncio.run(init_db())
            logger.info("Database initialized successfully")

            # Run the server
            logger.info("Starting DBMCP MCP server with FastMCP...")
            self.fastmcp.run("stdio")
        except Exception as e:
            print(f"Error running MCP server: {e}", file=sys.stderr)
            import traceback
            print(f"Full traceback: {traceback.format_exc()}", file=sys.stderr)
            sys.exit(1)


def main():
    """Main entry point for the MCP server."""
    server = DBMCPToolsServer()
    server.run()