from typing import Any, Dict, Union

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AuthenticationError
from app.core.jwt_validator import jwt_validator
from app.core.responses import create_error_response, create_success_response
from app.database import get_db
from app.models.schemas import UserLogin
from app.services.user_service import UserService

router = APIRouter()


class AuthRequest(BaseModel):
    """Request model for JWT token generation."""

    config: Union[str, Dict[str, Any]] = Field(
        ..., description="Config from tidd personas - can be string or object"
    )


class AuthResponse(BaseModel):
    """Response model for JWT token generation."""

    token: str = Field(..., description="Generated JWT token")
    expires_in_minutes: int = Field(..., description="Token expiration time in minutes")


@router.post("/auth", response_model=AuthResponse)
async def generate_token(request: AuthRequest):
    """
    Generate a new JWT token with the provided config.

    This endpoint accepts a config from tidd personas and creates a JWT token
    for dmcp access. We just generate an empty token since we don't need
    the actual config data.

    Args:
        request: AuthRequest containing the config

    Returns:
        AuthResponse with the generated token and expiration information
    """
    try:
        # Create token with empty payload - we don't need the config data
        # Check if request.config is present or not
        if request.config:
            token = jwt_validator.create_token(request.config)
        else:
            token = jwt_validator.create_token({})

        # Return the token with expiration info
        return AuthResponse(
            token=token, expires_in_minutes=jwt_validator.expiration_minutes
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=create_error_response(
                errors=[f"Token generation failed: {str(e)}"]
            ).model_dump(),
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
                ).model_dump(),
            )

        # Validate the token and get payload
        payload = jwt_validator.validate_token(auth_header)

        return JSONResponse(
            status_code=200,
            content=create_success_response(
                data={"payload": payload, "valid": True}
            ).model_dump(),
        )

    except AuthenticationError as e:
        return JSONResponse(
            status_code=401,
            content=create_error_response(
                errors=[f"Authentication failed: {e.message}"]
            ).model_dump(),
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content=create_error_response(
                errors=[f"Token validation error: {str(e)}"]
            ).model_dump(),
        )


@router.post("/auth/login", response_model=AuthResponse)
async def login_user(login_data: UserLogin, db: AsyncSession = Depends(get_db)):
    """Authenticate a user."""
    try:
        user_service = UserService(db)
        user = await user_service.authenticate_user(login_data)

        if not user:
            raise HTTPException(
                status_code=401,
                detail=create_error_response(
                    errors=["Invalid username or password"]
                ).model_dump(),
            )

        # Create token with empty payload - we don't need the config data
        token = jwt_validator.create_token(
            {"user_id": user.id, "username": user.username, "roles": user.roles}
        )

        # Return the token with expiration info
        return AuthResponse(
            token=token, expires_in_minutes=jwt_validator.expiration_minutes
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=create_error_response(
                errors=[f"Login failed: {str(e)}"]
            ).model_dump(),
        )
