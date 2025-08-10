"""Logging middleware for MCP operations."""

import logging
from fastmcp.server.middleware import Middleware, MiddlewareContext

logger = logging.getLogger(__name__)

class LoggingMiddleware(Middleware):
    """Middleware that logs all MCP operations."""
    
    async def on_message(self, context: MiddlewareContext, call_next):
        """Called for all MCP messages."""
        # print(f"+++++++ Processing {context.method} from {context.source}")
        
        result = await call_next(context)
        
        print(f"Completed {context.method}")
        # print(f"+++++++ From the LoggingMiddleware on_message: {result}")
        return result 