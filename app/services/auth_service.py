"""
Authentication service for JWT token management.
"""

from typing import Dict, Any
from app.core.jwt_validator import jwt_validator
from app.core.exceptions import AuthenticationError


class AuthService:
    """Service for handling authentication operations."""
    
    def __init__(self):
        self.jwt_validator = jwt_validator
        self.expiration_minutes = jwt_validator.expiration_minutes
    
    def create_token(self, payload: Dict[str, Any]) -> str:
        """Create a JWT token with the given payload."""
        return self.jwt_validator.create_token(payload)
    
    def validate_token(self, auth_header: str) -> Dict[str, Any]:
        """Validate a JWT token from an authorization header."""
        return self.jwt_validator.validate_token(auth_header)