#!/usr/bin/env python3
"""
Standalone MCP Server Runner for DBMCP.

This script runs the MCP server that exposes database operations as tools
for AI assistants and other MCP clients.
"""

import os
import sys

# server.py
from fastmcp import FastMCP
sys.stdout = sys.stderr
mcp = FastMCP("dbmcp")
current_dir = os.path.dirname(os.path.abspath(__file__))

@mcp.tool
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b

@mcp.tool
def hello_world() -> str:
    """Return a simple hello world message."""
    return "Hello, world!"

# Create a dummy prompt
@mcp.prompt()
async def create_epic():
    """Create a new epic. Provides guidance on how to create a new epic.
    """
    return "This is a prompt to create a new epic."

if __name__ == "__main__":
    mcp.run()