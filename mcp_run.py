#!/usr/bin/env python3
"""
MCP Server Runner

This script instantiates and starts the MCP server.
"""

from app.mcp.server import MCPServer


def main():
    """Main function to start the MCP server."""
    print("Starting MCP Server...")
    server = MCPServer()
    server.run()


if __name__ == "__main__":
    main() 