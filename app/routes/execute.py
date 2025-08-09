# from app.core.responses import api_response

# class HealthRouter:
#     def __init__(self, mcp):
#         self.mcp = mcp

#     def register_routes(self):


# @router.post("/{tool_id}", response_model=StandardAPIResponse)
# async def execute_named_tool(
#     tool_id: int,
#     execution_request: ToolExecutionRequest,
#     db: AsyncSession = Depends(get_db),
# ):
#     """Execute a named tool with parameters and pagination."""
#     try:
#         service = ToolExecutionService(db)
#         result = await service.execute_named_tool(
#             tool_id, execution_request.parameters, execution_request.pagination
#         )
#         if result.error:
#             raise_http_error(400, "Tool execution failed", [result.error])
#         return create_success_response(data=result)
#     except HTTPException:
#         raise
#     except Exception as e:
#         raise_http_error(500, "Internal server error", [str(e)])


# @router.post("/raw", response_model=StandardAPIResponse)
# async def execute_raw_query(
#     raw_request: RawQueryRequest,
#     db: AsyncSession = Depends(get_db),
# ):
#     """Execute a raw SQL query with parameters and pagination."""
#     try:
#         service = ToolExecutionService(db)
#         result = await service.execute_raw_query(
#             raw_request.datasource_id,
#             raw_request.sql,
#             raw_request.parameters,
#             raw_request.pagination,
#         )
#         return create_success_response(data=result)
#     except HTTPException:
#         raise
#     except Exception as e:
#         raise_http_error(500, "Internal server error", [str(e)]) 