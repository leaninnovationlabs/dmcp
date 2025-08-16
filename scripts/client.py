import asyncio
from fastmcp import Client, FastMCP

# In-memory server (ideal for testing)
server = FastMCP("TestServer")
client = Client(server)

# HTTP server
client = Client("http://127.0.0.1:8000/dbmcp")

async def main():
    async with client:
        # Basic server interaction
        await client.ping()
        
        # List available operations
        tools = await client.list_tools()
        print(tools)

        resources = await client.list_resources()
        prompts = await client.list_prompts()
        
        # Execute operations
        result = await client.call_tool("get_hotels", {"location": "Zurich"})

        # # Iterate over the result and print the keys and values
        for d in result.data['data']:
            print(str(d))


        # # result = await client.call_tool("demo_query", {"name": "Holi"})
        # print(result)

asyncio.run(main())