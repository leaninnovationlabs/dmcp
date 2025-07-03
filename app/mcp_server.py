# server.py
import asyncio
import sys
import types
from typing import Any, Callable, Dict, List
from fastmcp import FastMCP

from app.database import get_db
from app.services.tool_service import ToolService
from app.services.tool_execution_service import ToolExecutionService


class MCPServer:
    """MCP Server class that provides various tools and functionality."""
    
    def __init__(self, name: str = "Demo 🚀"):
        """Initialize the MCP server with the given name."""
        self.mcp = FastMCP(name)
        self._register_tools()
    
    def _register_tools(self):
        """Register all tools with the MCP server."""
        self.mcp.tool(self.hello_world)
        self._register_database_tools()
    
    def _register_database_tools(self):
        """Register tools from the database as MCP tools."""
        try:
            print("[DBMCP DEBUG] Starting to register database tools...", file=sys.stderr)
            tools = self._list_tools()
            print(f"[DBMCP DEBUG] Found {len(tools)} tools in database", file=sys.stderr)
            
            for tool in tools:
                try:
                    # Create a dynamic tool function for each database tool
                    tool_func = self._create_tool_function(tool)
                    self.mcp.tool(tool_func)
                    print(f"[DBMCP DEBUG] Registered tool: {tool['name']}", file=sys.stderr)
                    
                except Exception as tool_error:
                    print(f"[DBMCP ERROR] Failed to register tool {tool.get('name', 'unknown')}: {tool_error}", file=sys.stderr)
            
            print(f"[DBMCP DEBUG] Finished registering database tools", file=sys.stderr)
                
        except Exception as e:
            print(f"[DBMCP ERROR] Error registering database tools: {e}", file=sys.stderr)
            import traceback
            traceback.print_exc(file=sys.stderr)
    
    def hello_world(self, name: str = "World") -> str:
        """Say hello to the world"""
        return f"Hello, {name}!"
    
    def _create_tool_function(self, tool_data: Dict[str, Any]) -> Callable:
        """Create a dynamic tool function for the given tool data."""
        tool_id = tool_data['id']
        tool_name = tool_data['name']
        description = tool_data.get('description', f'Execute {tool_name}')
        
        if tool_data.get('parameters'):
            # Create function with parameters
            param_names = [param['name'] for param in tool_data['parameters']]
            
            # Validate and sanitize parameter names
            valid_param_names = []
            param_mapping = {}  # Maps sanitized names to original names
            
            for param_name in param_names:
                # Check if parameter name is a Python reserved keyword
                if param_name in ['class', 'def', 'import', 'from', 'as', 'in', 'is', 'if', 'else', 'elif', 'try', 'except', 'finally', 'with', 'for', 'while', 'return', 'yield', 'break', 'continue', 'pass', 'raise', 'assert', 'del', 'global', 'nonlocal', 'lambda', 'and', 'or', 'not', 'True', 'False', 'None']:
                    # Use a sanitized name for the function signature
                    sanitized_name = f"param_{param_name}"
                    valid_param_names.append(sanitized_name)
                    param_mapping[sanitized_name] = param_name
                    print(f"[DBMCP DEBUG] Sanitized parameter name '{param_name}' to '{sanitized_name}'", file=sys.stderr)
                else:
                    valid_param_names.append(param_name)
                    param_mapping[param_name] = param_name
            
            def tool_function(**kwargs):
                """Dynamic tool function with parameters."""
                # Map sanitized parameter names back to original names
                parameters = {}
                for sanitized_name, value in kwargs.items():
                    if value is not None and sanitized_name in param_mapping:
                        original_name = param_mapping[sanitized_name]
                        parameters[original_name] = value
                return self.execute_tool_by_id(tool_id, parameters)
            
            # Set function metadata
            tool_function.__name__ = tool_name
            tool_function.__doc__ = description
            
            # Create function signature with sanitized parameter names
            import inspect
            sig = inspect.signature(tool_function)
            new_params = []
            for param_name in valid_param_names:
                new_params.append(inspect.Parameter(
                    param_name, 
                    inspect.Parameter.POSITIONAL_OR_KEYWORD, 
                    default=None
                ))
            
            tool_function.__signature__ = sig.replace(parameters=new_params)
            print(f"[DBMCP DEBUG] Tool function signature: {tool_function.__signature__}", file=sys.stderr)
            return tool_function
        else:
            # No parameters, create simple function
            def tool_function():
                """Dynamic tool function without parameters."""
                return self.execute_tool_by_id(tool_id, {})
            
            tool_function.__name__ = tool_name
            tool_function.__doc__ = description
            return tool_function
    
    def execute_tool_by_id(self, tool_id: int, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a tool by its ID with parameters."""
        try:
            print(f"[DBMCP DEBUG] Executing tool {tool_id} with parameters: {parameters}", file=sys.stderr)
            
            async def _execute_tool_async():
                async for db in get_db():
                    service = ToolExecutionService(db)
                    result = await service.execute_named_tool(tool_id, parameters)
                    return result.model_dump()
            
            # Use a new event loop in a separate thread to avoid conflicts
            import concurrent.futures
            import threading
            
            def run_in_new_loop():
                new_loop = asyncio.new_event_loop()
                asyncio.set_event_loop(new_loop)
                try:
                    return new_loop.run_until_complete(_execute_tool_async())
                finally:
                    new_loop.close()
            
            # Run in a thread to avoid event loop conflicts
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(run_in_new_loop)
                result = future.result()
            
            print(f"[DBMCP DEBUG] Tool execution result: {result}", file=sys.stderr)
            return result
            
        except Exception as e:
            print(f"[DBMCP ERROR] Failed to execute tool {tool_id}: {e}", file=sys.stderr)
            import traceback
            traceback.print_exc(file=sys.stderr)
            return {
                "success": False,
                "data": [],
                "columns": [],
                "row_count": 0,
                "execution_time_ms": 0,
                "pagination": None,
                "error": str(e)
            }
    
    def _list_tools(self) -> List[Dict[str, Any]]:
        """Sync version of list_tools using a new event loop."""
        return asyncio.run(self._list_tools_async())
    
    async def _list_tools_async(self) -> List[Dict[str, Any]]:
        """Async version of list_tools."""
        async for db in get_db():
            tool_service = ToolService(db)
            tools = await tool_service.list_tools()
            return [tool.model_dump() for tool in tools]

    def run(self):
        """Start the MCP server."""
        self.mcp.run()
