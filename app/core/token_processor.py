from typing import Optional, Dict, Any
from fastapi import Header, HTTPException

from .jwt_validator import jwt_validator
from .responses import create_error_response
from .exceptions import AuthenticationError


async def get_payload(authorization: Optional[str] = Header(default=None)) -> Optional[Dict[str, Any]]:
    """
    FastAPI dependency that validates a Bearer token from the Authorization header
    and returns its decoded payload if present.

    - If the header is missing, returns None (so routes can be optionally public).
    - If the header is present but malformed/invalid, raises HTTP 401.
    """
    if not authorization:
        raise HTTPException(
            status_code=401,
            detail=create_error_response([
                "Invalid authorization header format. Use 'Bearer <token>'"
            ]).model_dump(),
        )

    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail=create_error_response([
                "Invalid authorization header format. Use 'Bearer <token>'"
            ]).model_dump(),
        )

    try:
        payload = jwt_validator.validate_token(authorization)
        return payload
    except AuthenticationError as e:
        raise HTTPException(
            status_code=401,
            detail=create_error_response([
                f"Authentication failed: Invalid or expired token provided"
            ]).model_dump(),
        )
    except Exception as e:
        raise HTTPException(
            status_code=401,
            detail=create_error_response([
                f"Authentication failed: Invalid or expired token provided"
            ]).model_dump(),
        )


