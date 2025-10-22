from fastmcp import FastMCP
from fastmcp.exceptions import ToolError
from fastmcp.server.middleware import Middleware, MiddlewareContext

mcp = FastMCP(
    name="MyServer",
    include_fastmcp_meta=True,  # include tags & FastMCP metadata under _meta._fastmcp
)


# Tag your tools so you can filter them later
@mcp.tool(tags={"public"})
def greet(name: str) -> str:
    return f"Hello, {name}!"


@mcp.tool(tags={"admin"})
def purge_cache() -> str:
    return "Cache purged."


# Yet to implement role based access control
class CustomizeToolsList(Middleware):
    async def on_list_tools(self, context: MiddlewareContext, call_next):
        tools = await call_next(context)  # list[Tool] (FastMCP component objects)

        # Example 1: filter by tag (hide admin-only tools for non-admins)
        # is_admin = False  # swap for your real check (token/claims, etc.)
        # if not is_admin:
        #     tools = [t for t in tools if "admin" not in t.tags]

        # Example 2: rename/retitle/add meta by returning transformed copies
        # new_tools = []
        # for t in tools:
        #     if t.name == "greet":
        #         t = Tool.from_tool(
        #             t,
        #             name="friendly_greet",
        #             description="Say hello to a user by name.",
        #             meta={"category": "examples", "priority": "low"},
        #             tags={"public", "examples"},
        #         )
        #     new_tools.append(t)

        return tools

    async def on_call_tool(self, context: MiddlewareContext, call_next):
        # Enforce the same policy at execution time
        blocked = {"purge_cache"}  # hide/deny execution for tools you filtered out
        if context.message.name in blocked:
            raise ToolError("Access denied")
        return await call_next(context)


mcp.add_middleware(CustomizeToolsList())
