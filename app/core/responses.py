import json
from datetime import datetime
from typing import Any, List, Optional

from starlette.responses import JSONResponse

from ..models.schemas import StandardAPIResponse


def create_success_response(data: Any = None, warnings: Optional[List[dict]] = None) -> StandardAPIResponse:
    """Create a standardized success response."""
    return StandardAPIResponse(data=data, success=True, errors=[], warnings=warnings or [])


def create_error_response(
    errors: List[str], data: Any = None, warnings: Optional[List[dict]] = None
) -> StandardAPIResponse:
    """Create a standardized error response."""
    error_list = [{"msg": error} for error in errors]
    return StandardAPIResponse(data=data, success=False, errors=error_list, warnings=warnings or [])


def create_warning_response(data: Any, warnings: List[str]) -> StandardAPIResponse:
    """Create a standardized response with warnings."""
    warning_list = [{"msg": warning} for warning in warnings]
    return StandardAPIResponse(data=data, success=True, errors=[], warnings=warning_list)


def raise_http_error(status_code: int, detail: str, errors: List[str] = None):
    """Raise an HTTPException with the given status code and details."""
    from fastapi import HTTPException

    if errors:
        detail = {"success": False, "errors": [{"msg": error} for error in errors]}
    else:
        detail = {"success": False, "detail": detail}

    raise HTTPException(status_code=status_code, detail=detail)


def api_response(data: Any = None, success: bool = True, errors: Optional[List[str]] = None) -> JSONResponse:
    """Universal HTTP JSON response envelope with datetime serialization."""

    def json_serializer(obj: Any):
        if isinstance(obj, datetime):
            return obj.isoformat()
        raise TypeError(f"Object of type {obj.__class__.__name__} is not JSON serializable")

    content = {"success": success, "data": data, "errors": errors or []}

    return JSONResponse(content=json.loads(json.dumps(content, default=json_serializer)))
