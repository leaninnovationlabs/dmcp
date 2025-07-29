"""Logging middleware for MCP operations."""

from fastmcp.server.middleware import Middleware, MiddlewareContext


class LoggingMiddleware(Middleware):
    """Middleware that logs all MCP operations."""
    
    async def on_message(self, context: MiddlewareContext, call_next):
        """Called for all MCP messages."""
        print(f"+++++++ Processing {context.method} from {context.source}")
        
        result = await call_next(context)
        
        print(f"Completed {context.method}")
        return result 