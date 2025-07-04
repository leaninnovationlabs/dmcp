import asyncio
from fastmcp import Client

client = Client("http://127.0.0.1:4200/dbmcp")

async def example():
    async with client:
        result = await client.call_tool("aws_cost_by_region", {})
        print(result)

if __name__ == "__main__":
    asyncio.run(example())