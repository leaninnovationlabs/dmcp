"""Server provider module for managing the MCP server instance.

This module provides a centralized way to access the MCP server instance
without creating circular dependencies.
"""

from typing import Optional

from app.mcp_server import MCPServer

# Global server instance (set during application startup)
_server_instance: Optional[MCPServer] = None


def set_server(server: MCPServer) -> None:
    """Set the global server instance.
    
    Args:
        server: The MCPServer instance to set.
    """
    global _server_instance
    _server_instance = server


def get_server() -> MCPServer:
    """Get the global server instance.
    
    Returns:
        The MCPServer instance.
        
    Raises:
        RuntimeError: If the server instance has not been set.
    """
    if _server_instance is None:
        raise RuntimeError(
            "Server instance has not been initialized. "
            "Ensure set_server() is called during application startup."
        )
    return _server_instance

