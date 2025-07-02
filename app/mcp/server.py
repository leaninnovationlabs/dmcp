# server.py
from fastmcp import FastMCP

mcp = FastMCP("Demo 🚀")

@mcp.tool
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b

@mcp.tool
def hello_world(name: str = "World") -> str:
    """Say hello to the world"""
    return f"Hello, {name}!"

if __name__ == "__main__":
    mcp.run()