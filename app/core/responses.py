from typing import Any, List, Optional
from ..models.schemas import StandardAPIResponse


def create_success_response(data: Any = None, warnings: Optional[List[dict]] = None) -> StandardAPIResponse:
    """Create a standardized success response."""
    return StandardAPIResponse(
        data=data,
        success=True,
        errors=[],
        warnings=warnings or []
    )


def create_error_response(errors: List[str], data: Any = None, warnings: Optional[List[dict]] = None) -> StandardAPIResponse:
    """Create a standardized error response."""
    error_list = [{"msg": error} for error in errors]
    return StandardAPIResponse(
        data=data,
        success=False,
        errors=error_list,
        warnings=warnings or []
    )


def create_warning_response(data: Any, warnings: List[str]) -> StandardAPIResponse:
    """Create a standardized response with warnings."""
    warning_list = [{"msg": warning} for warning in warnings]
    return StandardAPIResponse(
        data=data,
        success=True,
        errors=[],
        warnings=warning_list
    ) 