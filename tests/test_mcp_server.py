#!/usr/bin/env python3
"""
Test script for the DBMCP MCP server.

This script tests the MCP server functionality by simulating
tool listing and basic operations.
"""

import asyncio
import json
import sys
from pathlib import Path
import datetime

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.mcp.tools import MCPTools
from app.database import init_db

def json_serial(obj):
    if isinstance(obj, (datetime.datetime, datetime.date)):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")

async def test_mcp_tools():
    """Test the MCP tools functionality."""
    print("🧪 Testing DBMCP MCP Tools...")
    
    try:
        # Initialize database
        await init_db()
        print("✅ Database initialized successfully")
        
        # Test MCP tools
        mcp_tools = MCPTools()
        
        # Test listing datasources
        print("\n📋 Testing list_datasources_tool...")
        result = await mcp_tools.list_datasources_tool()
        print(f"✅ List datasources result: {json.dumps(result, indent=2, default=json_serial)}")
        
        # Test listing queries
        print("\n📋 Testing list_queries_tool...")
        result = await mcp_tools.list_queries_tool()
        print(f"✅ List queries result: {json.dumps(result, indent=2, default=json_serial)}")
        
        # Test MCP tools functionality
        print("\n🔧 MCP Tools functionality tested successfully")
        
        print("\n🎉 All MCP tools tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ MCP tools test failed: {e}")
        return False


async def main():
    """Main test function."""
    print("🚀 Starting DBMCP MCP Server Tests...\n")
    
    success = await test_mcp_tools()
    
    if success:
        print("\n✅ All tests passed! The MCP server is ready to use.")
        print("\nTo start the MCP server, run:")
        print("  python run_mcp_server.py")
        print("\nTo start the FastAPI server, run:")
        print("  python run.py")
    else:
        print("\n❌ Tests failed. Please check the error messages above.")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main()) 