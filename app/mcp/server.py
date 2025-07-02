# server.py
from fastmcp import FastMCP


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
    
    def add(self, a: int, b: int) -> int:
        """Add two numbers"""
        return a + b
    
    def hello_world(self, name: str = "World") -> str:
        """Say hello to the world"""
        return f"Hello, {name}!"
    
    def run(self):
        """Start the MCP server."""
        self.mcp.run()
