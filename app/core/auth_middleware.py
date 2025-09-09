"""FastAPI Authentication Middleware for Bearer Token validation."""

from typing import List
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from .jwt_validator import jwt_validator
from .exceptions import AuthenticationError
from .responses import create_error_response


class BearerTokenMiddleware(BaseHTTPMiddleware):
    """Middleware that validates Bearer tokens for API requests."""
    
    def __init__(self, app, excluded_paths: List[str] = None):
        """
        Initialize the middleware.
        
        Args:
            app: The FastAPI application instance
            excluded_paths: List of paths that don't require authentication
        """
        super().__init__(app)
        self.excluded_paths = excluded_paths 
    
    async def dispatch(self, request: Request, call_next) -> Response:
        """
        Process each request and validate Bearer token if required.
        
        Args:
            request: The incoming HTTP request
            call_next: The next middleware or route handler
            
        Returns:
            Response from the next handler or error response
        """

        # Skip authentication for CORS preflight requests
        if request.method == "OPTIONS":
            return await call_next(request)

        # Skip authentication for health endpoint and other excluded paths
        if any(request.url.path.startswith(path) for path in self.excluded_paths):
            return await call_next(request)
        
        # Skip authentication for static files and UI
        excluded_paths = ["/ui", "/dmcp/ui", "/dmcp/auth/login", "/favicon.ico", "/assets", "/vite.svg", ""]
        if any(request.url.path.startswith(path) for path in excluded_paths):
            return await call_next(request)
            
        # Get authorization header
        auth_header = request.headers.get("authorization", "")
        
        if not auth_header:
            return JSONResponse(
                status_code=401,
                content=create_error_response(
                    errors=["Missing authorization header. Please provide a Bearer token."]
                ).model_dump()
            )
        
        if not auth_header.startswith("Bearer "):
            return JSONResponse(
                status_code=401,
                content=create_error_response(
                    errors=["Invalid authorization header format. Use 'Bearer <token>'"]
                ).model_dump()
            )
        
        try:
            # Validate the JWT token
            decoded_payload = jwt_validator.validate_token(auth_header)
            
            # Add the decoded payload to request state for use in route handlers
            request.state.user = decoded_payload
            
        except AuthenticationError as e:
            return JSONResponse(
                status_code=401,
                content=create_error_response(
                    errors=[f"Authentication failed: {e.message}"]
                ).model_dump()
            )
        except Exception as e:
            return JSONResponse(
                status_code=401,
                content=create_error_response(
                    errors=[f"Token validation error: {str(e)}"]
                ).model_dump()
            )
        
        # Continue to the next middleware or route handler
        return await call_next(request) 