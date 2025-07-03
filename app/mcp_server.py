"""
MCP Server implementation for database tool execution.

This module provides a FastMCP server that dynamically registers and executes
database tools based on stored configurations.
"""

import asyncio
import concurrent.futures
import inspect
import sys
import traceback
from typing import Any, Callable, Dict, List, Optional

from fastmcp import FastMCP

from app.database import get_db
from app.services.tool_service import ToolService
from app.services.tool_execution_service import ToolExecutionService


# Constants
PYTHON_RESERVED_KEYWORDS = {
    'class', 'def', 'import', 'from', 'as', 'in', 'is', 'if', 'else', 'elif',
    'try', 'except', 'finally', 'with', 'for', 'while', 'return', 'yield',
    'break', 'continue', 'pass', 'raise', 'assert', 'del', 'global', 'nonlocal',
    'lambda', 'and', 'or', 'not', 'True', 'False', 'None'
}

DEFAULT_ERROR_RESPONSE = {
    "success": False,
    "data": [],
    "columns": [],
    "row_count": 0,
    "execution_time_ms": 0,
    "pagination": None,
    "error": ""
}


class MCPServer:
    """MCP Server class that provides various tools and functionality."""
    
    def __init__(self, name: str = "Demo 🚀"):
        """Initialize the MCP server with the given name."""
        self.mcp = FastMCP(name)
        self._register_tools()
    
    def _register_tools(self) -> None:
        """Register all tools with the MCP server."""
        self.mcp.tool(self.hello_world)
        self._register_database_tools()
    
    def _register_database_tools(self) -> None:
        """Register tools from the database as MCP tools."""
        try:
            self._log_debug("Starting to register database tools...")
            tools = self._list_tools()
            self._log_debug(f"Found {len(tools)} tools in database")
            
            for tool in tools:
                self._register_single_tool(tool)
            
            self._log_debug("Finished registering database tools")
                
        except Exception as e:
            self._log_error(f"Error registering database tools: {e}")
            traceback.print_exc(file=sys.stderr)
    
    def _register_single_tool(self, tool: Dict[str, Any]) -> None:
        """Register a single tool from the database."""
        try:
            tool_func = self._create_tool_function(tool)
            self.mcp.tool(tool_func)
            self._log_debug(f"Registered tool: {tool['name']}")
            
        except Exception as tool_error:
            self._log_error(f"Failed to register tool {tool.get('name', 'unknown')}: {tool_error}")
    
    def hello_world(self, name: str = "World") -> str:
        """Say hello to the world."""
        return f"Hello, {name}!"
    
    def _create_tool_function(self, tool_data: Dict[str, Any]) -> Callable:
        """Create a dynamic tool function for the given tool data."""
        tool_id = tool_data['id']
        tool_name = tool_data['name']
        description = tool_data.get('description', f'Execute {tool_name}')
        
        if tool_data.get('parameters'):
            return self._create_parameterized_tool_function(
                tool_id, tool_name, description, tool_data['parameters']
            )
        else:
            return self._create_simple_tool_function(tool_id, tool_name, description)
    
    def _create_parameterized_tool_function(
        self, 
        tool_id: int, 
        tool_name: str, 
        description: str, 
        parameters: List[Dict[str, Any]]
    ) -> Callable:
        """Create a tool function that accepts parameters."""
        param_names = [param['name'] for param in parameters]
        valid_param_names, param_mapping = self._sanitize_parameter_names(param_names)
        
        def tool_function(**kwargs):
            """Dynamic tool function with parameters."""
            parameters = self._map_parameters(kwargs, param_mapping)
            return self.execute_tool_by_id(tool_id, parameters)
        
        self._set_function_metadata(tool_function, tool_name, description, valid_param_names)
        return tool_function
    
    def _create_simple_tool_function(
        self, 
        tool_id: int, 
        tool_name: str, 
        description: str
    ) -> Callable:
        """Create a tool function without parameters."""
        def tool_function():
            """Dynamic tool function without parameters."""
            return self.execute_tool_by_id(tool_id, {})
        
        self._set_function_metadata(tool_function, tool_name, description)
        return tool_function
    
    def _sanitize_parameter_names(
        self, 
        param_names: List[str]
    ) -> tuple[List[str], Dict[str, str]]:
        """Sanitize parameter names to avoid Python reserved keywords."""
        valid_param_names = []
        param_mapping = {}
        
        for param_name in param_names:
            if param_name in PYTHON_RESERVED_KEYWORDS:
                sanitized_name = f"param_{param_name}"
                valid_param_names.append(sanitized_name)
                param_mapping[sanitized_name] = param_name
                self._log_debug(f"Sanitized parameter name '{param_name}' to '{sanitized_name}'")
            else:
                valid_param_names.append(param_name)
                param_mapping[param_name] = param_name
        
        return valid_param_names, param_mapping
    
    def _map_parameters(
        self, 
        kwargs: Dict[str, Any], 
        param_mapping: Dict[str, str]
    ) -> Dict[str, Any]:
        """Map sanitized parameter names back to original names."""
        parameters = {}
        for sanitized_name, value in kwargs.items():
            if value is not None and sanitized_name in param_mapping:
                original_name = param_mapping[sanitized_name]
                parameters[original_name] = value
        return parameters
    
    def _set_function_metadata(
        self, 
        func: Callable, 
        name: str, 
        description: str, 
        param_names: Optional[List[str]] = None
    ) -> None:
        """Set metadata for the tool function."""
        func.__name__ = name
        func.__doc__ = description
        
        if param_names:
            self._set_function_signature(func, param_names)
    
    def _set_function_signature(self, func: Callable, param_names: List[str]) -> None:
        """Set the function signature with the given parameter names."""
        sig = inspect.signature(func)
        new_params = [
            inspect.Parameter(
                param_name, 
                inspect.Parameter.POSITIONAL_OR_KEYWORD, 
                default=None
            )
            for param_name in param_names
        ]
        
        func.__signature__ = sig.replace(parameters=new_params)
        self._log_debug(f"Tool function signature: {func.__signature__}")
    
    def execute_tool_by_id(self, tool_id: int, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a tool by its ID with parameters."""
        try:
            self._log_debug(f"Executing tool {tool_id} with parameters: {parameters}")
            
            result = self._execute_tool_async(tool_id, parameters)
            self._log_debug(f"Tool execution result: {result}")
            return result
            
        except Exception as e:
            self._log_error(f"Failed to execute tool {tool_id}: {e}")
            traceback.print_exc(file=sys.stderr)
            return {**DEFAULT_ERROR_RESPONSE, "error": str(e)}
    
    def _execute_tool_async(self, tool_id: int, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute tool asynchronously in a separate thread."""
        async def _execute_tool_async():
            async for db in get_db():
                service = ToolExecutionService(db)
                result = await service.execute_named_tool(tool_id, parameters)
                return result.model_dump()
        
        def run_in_new_loop():
            new_loop = asyncio.new_event_loop()
            asyncio.set_event_loop(new_loop)
            try:
                return new_loop.run_until_complete(_execute_tool_async())
            finally:
                new_loop.close()
        
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(run_in_new_loop)
            return future.result()
    
    def _list_tools(self) -> List[Dict[str, Any]]:
        """Get list of tools from database using sync wrapper."""
        return asyncio.run(self._list_tools_async())
    
    async def _list_tools_async(self) -> List[Dict[str, Any]]:
        """Get list of tools from database asynchronously."""
        async for db in get_db():
            tool_service = ToolService(db)
            tools = await tool_service.list_tools()
            return [tool.model_dump() for tool in tools]
    
    def _log_debug(self, message: str) -> None:
        """Log debug message to stderr."""
        print(f"[DBMCP DEBUG] {message}", file=sys.stderr)
    
    def _log_error(self, message: str) -> None:
        """Log error message to stderr."""
        print(f"[DBMCP ERROR] {message}", file=sys.stderr)

    def run(self) -> None:
        """Start the MCP server."""
        self.mcp.run()
