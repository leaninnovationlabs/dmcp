"""Logging middleware for MCP operations."""

import logging
from fastmcp.server.middleware import Middleware, MiddlewareContext

logger = logging.getLogger(__name__)

class LoggingMiddleware(Middleware):
    """Middleware that logs all MCP operations."""
    
    async def on_message(self, context: MiddlewareContext, call_next):
        """Called for all MCP messages."""
        logger.debug(f"+++++++ Processing {context.method} from {context.source}")
        
        result = await call_next(context)
        
        logger.debug(f"Completed {context.method}")
        return result 