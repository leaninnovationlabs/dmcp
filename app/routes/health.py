from app.core.responses import api_response

class HealthRouter:
    def __init__(self, mcp):
        self.mcp = mcp

    def register_routes(self):
        @self.mcp.custom_route("/health", methods=["GET"])
        async def health_check(request):
            """Health check endpoint."""
            return api_response({"status": "healthy", "message": "DBMCP server is running"})

