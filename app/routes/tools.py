import json
import traceback

from fastapi import HTTPException
from app.core.exceptions import AuthenticationError
from app.core.responses import api_response, create_success_response, raise_http_error
from app.core.token_processor import get_payload
from app.models.schemas import ToolExecutionRequest
from app.services.tool_execution_service import ToolExecutionService
from app.services.tool_service import ToolService
from app.database import get_db

class ToolsRouter:
    def __init__(self, mcp):
        self.mcp = mcp

    def register_routes(self):

        @self.mcp.custom_route("/tools", methods=["GET"])
        async def list_tools(request):

            try:
                payload = await get_payload(request)

                """List all tools."""
                async for db in get_db():
                    service = ToolService(db)
                    result = await service.list_tools()
                    return api_response([tool.model_dump() for tool in result])
            except AuthenticationError as e:
                return api_response(None, False, [f"Authentication failed: {e.message}"])
            except Exception as e:
                return api_response(None, False, [f"Failed to list tools: {str(e)}"])

        @self.mcp.custom_route("/tools", methods=["POST"])
        async def create_tool(request):
            """Create a new tool."""
            try:
                payload = await get_payload(request)
                body = await request.body()
                data = json.loads(body) if body else {}
                
                async for db in get_db():
                    service = ToolService(db)
                    from app.models.schemas import ToolCreate
                    tool_data = ToolCreate(**data)
                    result = await service.create_tool(tool_data)
                    return api_response(result.model_dump())
            except AuthenticationError as e:
                return api_response(None, False, [f"Authentication failed: {e.message}"])
            except Exception as e:
                return api_response(None, False, [f"Failed to create tool: {str(e)}"])


        @self.mcp.custom_route("/tools/{tool_id}", methods=["GET"])
        async def get_tool(request):
            """Get specific tool."""

            try:
                payload = await get_payload(request)
                tool_id = int(request.path_params.get("tool_id"))
                async for db in get_db():
                    service = ToolService(db)
                    tool = await service.get_tool(tool_id)
                    if not tool:
                        return api_response(None, False, ["Tool not found"])
                        return api_response(tool.model_dump())
            except AuthenticationError as e:
                return api_response(None, False, [f"Authentication failed: {e.message}"])
            except Exception as e:
                return api_response(None, False, [f"Failed to get tool: {str(e)}"])

        @self.mcp.custom_route("/tools/execute/{tool_id}", methods=["POST"])
        async def execute_named_tool(request):
            """Execute a named tool with parameters and pagination."""
            try:
                payload = await get_payload(request)
                body = await request.body()
                execution_request = json.loads(body) if body else {}
                print(f"+++++++ From the execute_named_tool Request: {execution_request}")
                tool_id = int(request.path_params.get("tool_id"))

                async for db in get_db():   
                    service = ToolExecutionService(db)
                    result = await service.execute_named_tool(
                        tool_id, execution_request["parameters"], execution_request["pagination"]
                    )

                    print(f"+++++++ From the execute_named_tool Result: {result}")
                    if result.error:
                        raise_http_error(400, "Tool execution failed", [result.error])
                    return api_response(result.model_dump())
            except AuthenticationError as e:
                return api_response(None, False, [f"Authentication failed: {e.message}"])
            except HTTPException:
                raise
            except Exception as e:
                print(e)
                print(traceback.format_exc())
                raise_http_error(500, "Internal server error", [str(e)])
