from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
from typing import Dict, Any
from pydantic import BaseModel, Field

from app.core.jwt_validator import jwt_validator
from app.core.responses import create_success_response, create_error_response
from app.core.exceptions import AuthenticationError

router = APIRouter()


class AuthRequest(BaseModel):
    """Request model for JWT token generation."""
    payload: Dict[str, Any] = Field(..., description="Dynamic payload to include in JWT token")


class AuthResponse(BaseModel):
    """Response model for JWT token generation."""
    token: str = Field(..., description="Generated JWT token")
    expires_in_minutes: int = Field(..., description="Token expiration time in minutes")


@router.post("/auth", response_model=AuthResponse)
async def generate_token(request: AuthRequest):
    """
    Generate a new JWT token with the provided dynamic payload.
    
    This endpoint accepts any JSON payload and creates a JWT token containing
    that payload along with standard JWT claims (exp, iat).
    
    Args:
        request: AuthRequest containing the dynamic payload
        
    Returns:
        AuthResponse with the generated token and expiration information
    """
    try:
        # Create token with the provided payload
        token = jwt_validator.create_token(request.payload)
        
        # Return the token with expiration info
        return AuthResponse(
            token=token,
            expires_in_minutes=jwt_validator.expiration_minutes
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=create_error_response(
                errors=[f"Token generation failed: {str(e)}"]
            ).model_dump()
        )


@router.get("/auth/validate")
async def validate_token(request: Request):
    """
    Validate a JWT token and return its payload.
    
    This endpoint accepts a token in the Authorization header and returns
    the decoded payload if the token is valid.
    
    Returns:
        StandardAPIResponse with the token payload or error details
    """
    try:
        # Get the Authorization header
        auth_header = request.headers.get("Authorization", "")
        
        if not auth_header:
            return JSONResponse(
                status_code=401,
                content=create_error_response(
                    errors=["Authorization header is required"]
                ).model_dump()
            )
        
        # Validate the token and get payload
        payload = jwt_validator.validate_token(auth_header)
        
        return JSONResponse(
            status_code=200,
            content=create_success_response(
                data={
                    "payload": payload,
                    "valid": True
                }
            ).model_dump()
        )
        
    except AuthenticationError as e:
        return JSONResponse(
            status_code=401,
            content=create_error_response(
                errors=[f"Authentication failed: {e.message}"]
            ).model_dump()
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content=create_error_response(
                errors=[f"Token validation error: {str(e)}"]
            ).model_dump()
        ) 