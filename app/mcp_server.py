# server.py
import asyncio
import sys
from typing import Any, Callable, Dict, List
from fastmcp import FastMCP

from app.database import AsyncSessionLocal
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
        self.mcp.tool(self.add)
        self.mcp.tool(self.hello_world)
        # self.mcp.tool(self.refresh_tools)
        self._register_database_tools()
    
    def _register_database_tools(self):
        """Register tools from the database as MCP tools."""
        try:
            print("[DBMCP DEBUG] Starting to register database tools...", file=sys.stderr)
            tools = self._list_tools_sync()
            print(f"[DBMCP DEBUG] Found {len(tools)} tools in database", file=sys.stderr)
            
            for tool in tools:
                try:
                    # Create a dynamic tool function for each database tool
                    def create_tool_function(tool_data):
                        # Create function signature based on tool parameters
                        if tool_data.get('parameters'):
                            # Create explicit parameters for each tool parameter
                            param_names = [param['name'] for param in tool_data['parameters']]
                            
                            # Create function with explicit parameters
                            param_str = ', '.join([f"{name}=None" for name in param_names])
                            func_code = f"""
def {tool_data['name']}({param_str}):
    \"\"\"{tool_data.get('description', f'Execute {tool_data['name']}')}\"\"\"
    parameters = {{}}
    for name in {param_names}:
        if locals()[name] is not None:
            parameters[name] = locals()[name]
    return self.execute_tool_by_id({tool_data['id']}, parameters)
"""
                            # Execute the function definition
                            local_vars = {'self': self}
                            exec(func_code, globals(), local_vars)
                            return local_vars[tool_data['name']]
                        else:
                            # No parameters, create simple function
                            def tool_function():
                                return self.execute_tool_by_id(tool_data['id'], {})
                            
                            tool_function.__name__ = tool_data['name']
                            tool_function.__doc__ = tool_data.get('description', f"Execute {tool_data['name']}")
                            return tool_function
                    
                    # Register the tool
                    tool_func = create_tool_function(tool)
                    self.mcp.tool(tool_func)
                    print(f"[DBMCP DEBUG] Registered tool: {tool['name']}", file=sys.stderr)
                    
                except Exception as tool_error:
                    print(f"[DBMCP ERROR] Failed to register tool {tool.get('name', 'unknown')}: {tool_error}", file=sys.stderr)
            
            print(f"[DBMCP DEBUG] Finished registering database tools", file=sys.stderr)
                
        except Exception as e:
            print(f"[DBMCP ERROR] Error registering database tools: {e}", file=sys.stderr)
            import traceback
            traceback.print_exc(file=sys.stderr)
    
    def add(self, a: int, b: int) -> int:
        """Add two numbers"""
        return a + b
    
    def hello_world(self, name: str = "World") -> str:
        """Say hello to the world"""
        return f"Hello, {name}!"
    
    def refresh_tools(self) -> str:
        """Refresh the list of tools from the database."""
        try:
            print("[DBMCP DEBUG] Refreshing tools...", file=sys.stderr)
            self._register_database_tools()
            return "Tools refreshed successfully"
        except Exception as e:
            print(f"[DBMCP ERROR] Failed to refresh tools: {e}", file=sys.stderr)
            return f"Failed to refresh tools: {e}"
    
    def execute_tool_by_id(self, tool_id: int, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a tool by its ID with parameters."""
        try:
            print(f"[DBMCP DEBUG] Executing tool {tool_id} with parameters: {parameters}", file=sys.stderr)
            
            async def _execute_tool_async():
                async with AsyncSessionLocal() as db:
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
    
    def _list_tools_sync(self) -> List[Dict[str, Any]]:
        """Sync version of list_tools using a new event loop."""
        async def _list_tools_async():
            async with AsyncSessionLocal() as db:
                tool_service = ToolService(db)
                tools = await tool_service.list_tools()
                return [tool.model_dump() for tool in tools]
        
        return asyncio.run(_list_tools_async())

    def run(self):
        """Start the MCP server."""
        self.mcp.run()
