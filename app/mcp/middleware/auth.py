"""Authentication middleware for MCP operations."""

import logging
from fastmcp.server.dependencies import get_http_headers
from fastmcp.server.middleware import Middleware, MiddlewareContext

from app.core.jwt_validator import jwt_validator
from app.core.exceptions import AuthenticationError
from app.core.config import settings

logger = logging.getLogger(__name__)


class AuthMiddleware(Middleware):
    """Middleware that checks for authentication."""
    
    async def on_message(self, context: MiddlewareContext, call_next):
        """Called for all MCP messages."""

        headers = get_http_headers()

        # # Get authorization header, which holds the key
        auth_header = headers.get("authorization", "")

        # Skip the authentication check for the tools/list method
        if context.method != 'tools/list' :
            try:
                decoded_payload = jwt_validator.validate_token(auth_header)
                logger.debug(f"User ID: {decoded_payload}")
            except AuthenticationError as e:
                logger.warning(f"Authentication failed: {e.message}")
                return {"error": True}
            
        result = await call_next(context)
        
        logger.info(f"Completed {context.method}")
        return result