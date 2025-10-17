"""JWT token validation and management."""

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

import jwt

from app.core.config import settings
from app.core.exceptions import AuthenticationError


class JWTValidator:
    """JWT token validator using configured secret key and algorithm."""

    def __init__(self):
        """Initialize JWT validator with settings from config."""
        self.secret_key = settings.secret_key
        self.algorithm = settings.jwt_algorithm
        self.expiration_minutes = settings.jwt_expiration_minutes

    def create_token(self, payload: Dict[str, Any]) -> str:
        """
        Create a JWT token with the given payload.

        Args:
            payload: Dictionary containing the token claims

        Returns:
            Encoded JWT token string
        """
        # Add expiration time to payload
        expiration = datetime.now(timezone.utc) + timedelta(minutes=self.expiration_minutes)
        payload.update({"exp": expiration, "iat": datetime.now(timezone.utc)})

        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

    def validate_token(self, token: str) -> Dict[str, Any]:
        """
        Validate and decode a JWT token.

        Args:
            token: JWT token string to validate

        Returns:
            Decoded token payload

        Raises:
            AuthenticationError: If token is invalid, expired, or malformed
        """
        try:
            # Remove 'Bearer ' prefix if present
            if token.startswith("Bearer "):
                token = token[7:]

            # Decode and validate the token
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])

            return payload

        except jwt.ExpiredSignatureError:
            raise AuthenticationError("Token has expired")
        except jwt.InvalidTokenError:
            raise AuthenticationError("Invalid token")
        except Exception as e:
            raise AuthenticationError(f"Token validation failed: {str(e)}")

    def is_token_valid(self, token: str) -> bool:
        """
        Check if a token is valid without raising exceptions.

        Args:
            token: JWT token string to validate

        Returns:
            True if token is valid, False otherwise
        """
        try:
            self.validate_token(token)
            return True
        except AuthenticationError:
            return False

    def get_token_payload(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Get token payload without validation (for debugging purposes only).

        Args:
            token: JWT token string

        Returns:
            Decoded payload or None if token is malformed
        """
        try:
            # Remove 'Bearer ' prefix if present
            if token.startswith("Bearer "):
                token = token[7:]

            # Decode without verification (use with caution)
            payload = jwt.decode(token, options={"verify_signature": False})
            return payload
        except Exception:
            return None


# Global JWT validator instance
jwt_validator = JWTValidator()
