import json

from app.core.jwt_validator import jwt_validator
from app.core.responses import api_response
from app.services.auth_service import AuthService


class AuthRouter:
    def __init__(self, mcp):
        self.mcp = mcp

    def register_routes(self):
        @self.mcp.custom_route("/auth", methods=["POST"])
        async def generate_token(request):
            """Generate JWT token endpoint."""
            try:
                body = await request.body()
                payload = json.loads(body) if body else {}
                
                auth_service = AuthService()
                token = auth_service.create_token(payload)
                
                return api_response({
                    "token": token,
                    "expires_in_minutes": auth_service.expiration_minutes
                })
            except Exception as e:
                return api_response(None, False, [f"Token generation failed: {str(e)}"])


        @self.mcp.custom_route("/auth/validate", methods=["GET"])
        async def validate_token(request):
            """Validate JWT token endpoint."""  
            auth_header = request.headers.get("authorization", "")
            
            if not auth_header:
                return api_response(None, False, ["Authorization header is required"])
            
            auth_service = AuthService()
            try:
                payload = auth_service.validate_token(auth_header)
                return api_response({"payload": payload, "valid": True})
            except Exception as e:
                return api_response(None, False, [f"Authentication failed: {str(e)}"])
