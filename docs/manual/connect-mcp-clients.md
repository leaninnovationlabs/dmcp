---
outline: deep
---

# Connect from MCP Clients

Once you have configured your DataSources and created Tools, you can connect AI assistants to your DBMCP server through the Model Context Protocol (MCP). This allows AI models to execute your database queries using natural language.

## What is MCP?

The Model Context Protocol (MCP) is a standard that enables AI assistants to interact with external tools and data sources. DBMCP implements this protocol to expose your database tools to AI models.

## MCP Server Setup

### Starting the MCP Server

DBMCP provides an MCP server that exposes your tools to AI assistants:

```bash
uv run mcp_run.py
```

By default, the MCP server runs on port 4200 with the `/dbmcp/mcp` prefix.

### Server Configuration

The MCP server supports two transport modes:

#### 1. HTTP Transport (Default)
- **URL**: `http://127.0.0.1:4200/dbmcp`
- **Authentication**: Bearer token required
- **Use Case**: Web-based MCP clients, remote connections

#### 2. stdio Transport
- **Transport**: Standard input/output
- **Authentication**: Disabled (development only)
- **Use Case**: Local AI assistants like Claude Desktop

## Connecting AI Assistants


### 1. MCP Inspector

MCP Inspector is a web-based tool for testing MCP servers.

#### Setup

1. Install MCP Inspector:
```bash
npm install -g @modelcontextprotocol/inspector
```

2. Launch the inspector:
```bash
npx @modelcontextprotocol/inspector
```

3. Configure the connection:
   - **URL**: `http://127.0.0.1:4200/dbmcp`
   - **Header Name**: `Authorization`
   - **Header Value**: `Bearer YOUR_TOKEN`


### 2. Claude Desktop

Claude Desktop is a popular AI assistant that supports MCP servers.
**Note**: Claude Desktop right now supports only OAuth for http transport, you will have to use stdio transport for local development.

#### Configuration

Add the following to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "dbmcp": {
      "command": "/path/to/uv",
      "args": [
        "--directory",
        "/path/to/dbmcp",
        "run",
        "mcp_run.py"
      ],
      "env": {
        "TRANSPORT": "stdio"
      }
    }
  }
}
```



### 3. Custom MCP Clients

You can build custom MCP clients using the MCP protocol specification.

#### Python Example

**stdio Transport (Local Development)**

```python
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def main():
    # Connect to DBMCP server via stdio
    server = StdioServerParameters(
        command="uv",
        args=["--directory", "/path/to/dbmcp", "run", "mcp_run.py"],
        env={"TRANSPORT": "stdio"}
    )
    
    async with stdio_client(server) as (read, write):
        async with ClientSession(read, write) as session:
            # List available tools
            tools = await session.list_tools()
            print("Available tools:", tools)
            
            # Execute a tool
            result = await session.call_tool(
                name="get_user_count",
                arguments={}
            )
            print("Result:", result)

asyncio.run(main())
```

**HTTP Transport (Remote/Web-based)**

```python
import asyncio
import aiohttp
from mcp import ClientSession
from mcp.client.http import http_client

async def main():
    # Connect to DBMCP server via HTTP
    server_url = "http://127.0.0.1:4200/dbmcp"
    headers = {
        "Authorization": "Bearer YOUR_TOKEN_HERE",
        "Content-Type": "application/json"
    }
    
    async with aiohttp.ClientSession() as http_session:
        async with http_client(http_session, server_url, headers) as (read, write):
            async with ClientSession(read, write) as session:
                # List available tools
                tools = await session.list_tools()
                print("Available tools:", tools)
                
                # Execute a tool
                result = await session.call_tool(
                    name="get_user_count",
                    arguments={}
                )
                print("Result:", result)

asyncio.run(main())
```

#### JavaScript Example

**stdio Transport (Local Development)**

```javascript
import { Client } from '@modelcontextprotocol/sdk/client/index.js';
import { StdioServerParameters } from '@modelcontextprotocol/sdk/server/index.js';

async function main() {
    const server = new StdioServerParameters({
        command: 'uv',
        args: ['--directory', '/path/to/dbmcp', 'run', 'mcp_run.py'],
        env: { TRANSPORT: 'stdio' }
    });
    
    const client = new Client(server);
    await client.connect();
    
    // List tools
    const tools = await client.listTools();
    console.log('Available tools:', tools);
    
    // Execute tool
    const result = await client.callTool('get_user_count', {});
    console.log('Result:', result);
    
    await client.close();
}

main();
```

**HTTP Transport (Remote/Web-based)**

```javascript
import { Client } from '@modelcontextprotocol/sdk/client/index.js';
import { HttpServerParameters } from '@modelcontextprotocol/sdk/server/index.js';

async function main() {
    const server = new HttpServerParameters({
        url: 'http://127.0.0.1:4200/dbmcp',
        headers: {
            'Authorization': 'Bearer YOUR_TOKEN_HERE',
            'Content-Type': 'application/json'
        }
    });
    
    const client = new Client(server);
    await client.connect();
    
    // List tools
    const tools = await client.listTools();
    console.log('Available tools:', tools);
    
    // Execute tool
    const result = await client.callTool('get_user_count', {});
    console.log('Result:', result);
    
    await client.close();
}

main();
```

## Authentication

### Token Generation

Generate an authentication token:

```bash
uv run scripts/apptoken.py
```

### Using Tokens

#### HTTP Transport
Include the token in your request headers:

```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
     http://127.0.0.1:4200/dbmcp/tools
```

#### stdio Transport
For local development, authentication is disabled when using stdio transport.

## Tool Discovery

### Listing Available Tools

MCP clients can discover available tools through the protocol:

```python
# List all tools
tools = await session.list_tools()

for tool in tools:
    print(f"Tool: {tool.name}")
    print(f"Description: {tool.description}")
    print(f"Parameters: {tool.inputSchema}")
    print("---")
```

### Tool Metadata

Each tool includes metadata that helps AI assistants understand how to use it:

```json
{
  "name": "get_users_by_status",
  "description": "Get users filtered by their status",
  "inputSchema": {
    "type": "object",
    "properties": {
      "status": {
        "type": "string",
        "description": "User status to filter by",
        "enum": ["active", "inactive", "suspended"]
      }
    },
    "required": ["status"]
  }
}
```

## Usage Examples

### 1. Business Intelligence

**User Query**: "Show me sales analytics for the last 30 days"

**AI Response**: I'll use the sales_analytics tool to get that information for you.

**Tool Execution**:
```json
{
  "name": "sales_analytics",
  "arguments": {
    "start_date": "2024-01-01",
    "end_date": "2024-01-31"
  }
}
```

### 2. Data Exploration

**User Query**: "Find all users with email addresses containing 'gmail.com'"

**AI Response**: I'll search for users with Gmail addresses using the search_users tool.

**Tool Execution**:
```json
{
  "name": "search_users",
  "arguments": {
    "search_term": "gmail.com",
    "limit": 50
  }
}
```

### 3. Administrative Tasks

**User Query**: "How many active users do we have?"

**AI Response**: Let me check the current user count using the get_user_count tool.

**Tool Execution**:
```json
{
  "name": "get_user_count",
  "arguments": {}
}
```



## Troubleshooting

### Common Issues

#### 1. Connection Refused
- Ensure the MCP server is running
- Check the port configuration
- Verify firewall settings

#### 2. Authentication Errors
- Generate a new token: `uv run scripts/apptoken.py`
- Check token format: `Bearer YOUR_TOKEN`
- Verify token hasn't expired

#### 3. Tool Not Found
- Check if the tool exists in your DBMCP instance
- Verify tool names match exactly
- Ensure the tool is properly configured

#### 4. Parameter Errors
- Check parameter names and types
- Verify required parameters are provided
- Test with the MCP Inspector first

### Debugging Tips

1. **Use MCP Inspector**
   - Test tools before connecting to AI assistants
   - Verify parameter validation
   - Check error messages

2. **Enable Debug Logging**
   ```bash
   LOG_LEVEL=DEBUG
   ```

3. **Test with Simple Tools**
   - Start with basic query tools
   - Verify database connectivity
   - Check tool execution

4. **Monitor Server Logs**
   - Watch for connection attempts
   - Check for authentication errors
   - Monitor tool execution


## Advanced Configuration

### Custom MCP Server

You can customize the MCP server configuration:

```python
# Custom server configuration
import os
from app.mcp_server import create_mcp_server

# Set custom environment
os.environ["MCP_HOST"] = "0.0.0.0"
os.environ["MCP_PORT"] = "4200"
os.environ["MCP_PREFIX"] = "/custom/mcp"

# Create and run server
server = create_mcp_server()
server.run()
```

### Load Balancing

For high-traffic scenarios, you can run multiple MCP server instances:

```bash
# Start multiple instances
uv run mcp_run.py --port 4200
uv run mcp_run.py --port 4201
uv run mcp_run.py --port 4202
```



## Next Steps

Now that you have connected your MCP clients, you can:

1. **Test your tools** - Use the MCP Inspector to verify functionality
2. **Optimize performance** - Monitor and improve tool efficiency
3. **Scale your setup** - Add more tools and datasources
4. **Integrate with workflows** - Connect to other MCP servers

Your DBMCP setup is now complete! You can start using AI assistants to interact with your databases through natural language. 