from typing import Any, Dict, Optional

from fastapi import HTTPException

from .exceptions import AuthenticationError
from .jwt_validator import jwt_validator
from .responses import create_error_response


async def get_payload(request: Any) -> Optional[Dict[str, Any]]:
    """
    Extract the Authorization header from the given request, validate the token,
    and return the decoded payload.

    Raises HTTP 401 if the header is missing or malformed, or if validation fails.
    """
    authorization: Optional[str] = None

    if request is not None and hasattr(request, "headers") and request.headers is not None:
        # Some frameworks provide case-insensitive headers mapping
        authorization = request.headers.get("authorization")

    if not authorization or not isinstance(authorization, str) or not authorization.strip():
        raise HTTPException(
            status_code=401,
            detail=create_error_response(["Invalid authorization header format. Use 'Bearer <token>'"]).model_dump(),
        )

    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail=create_error_response(["Invalid authorization header format. Use 'Bearer <token>'"]).model_dump(),
        )

    try:
        payload = jwt_validator.validate_token(authorization)
        return payload
    except AuthenticationError:
        raise HTTPException(
            status_code=401,
            detail=create_error_response(["Authentication failed: Invalid or expired token provided"]).model_dump(),
        )
    except Exception:
        raise HTTPException(
            status_code=401,
            detail=create_error_response(["Authentication failed: Invalid or expired token provided"]).model_dump(),
        )
