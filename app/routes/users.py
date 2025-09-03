from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import JSONResponse
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..services.user_service import UserService
from ..models.schemas import (
    UserCreate, UserUpdate, UserResponse, UserLogin, 
    UserPasswordChange, StandardAPIResponse
)
from ..core.responses import create_success_response, create_error_response
from ..core.exceptions import DMCPException

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", response_model=StandardAPIResponse)
async def create_user(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new user."""
    try:
        user_service = UserService(db)
        user = await user_service.create_user(user_data)
        
        return create_success_response(
            data=user
        )
    except DMCPException as e:
        raise HTTPException(
            status_code=400,
            detail=create_error_response(
                errors=[str(e)]
            ).model_dump()
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=create_error_response(
                errors=[f"Failed to create user: {str(e)}"]
            ).model_dump()
        )


@router.get("/", response_model=StandardAPIResponse)
async def get_all_users(
    db: AsyncSession = Depends(get_db)
):
    """Get all users."""
    try:
        user_service = UserService(db)
        users = await user_service.get_all_users()
        print(f"Users: {users}")
        return create_success_response(
            data=users
        )
    except Exception as e:
        print(f"Failed to get users: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=create_error_response(
                errors=[f"Failed to get users: {str(e)}"]
            ).model_dump()
        )


@router.get("/{user_id}", response_model=StandardAPIResponse)
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get a user by ID."""
    try:
        user_service = UserService(db)
        user = await user_service.get_user_by_id(user_id)
        
        if not user:
            raise HTTPException(
                status_code=404,
                detail=create_error_response(
                    errors=["User not found"]
                ).model_dump()
            )
        
        return create_success_response(
            data=user
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=create_error_response(
                errors=[f"Failed to get user: {str(e)}"]
            ).model_dump()
        )


@router.put("/{user_id}", response_model=StandardAPIResponse)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update a user."""
    try:
        user_service = UserService(db)
        user = await user_service.update_user(user_id, user_data)
        
        if not user:
            raise HTTPException(
                status_code=404,
                detail=create_error_response(
                    errors=["User not found"]
                ).model_dump()
            )
        
        return create_success_response(
            data=user
        )
    except HTTPException:
        raise
    except DMCPException as e:
        raise HTTPException(
            status_code=400,
            detail=create_error_response(
                errors=[str(e)]
            ).model_dump()
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=create_error_response(
                errors=[f"Failed to update user: {str(e)}"]
            ).model_dump()
        )


@router.delete("/{user_id}", response_model=StandardAPIResponse)
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Delete a user."""
    try:
        user_service = UserService(db)
        success = await user_service.delete_user(user_id)
        
        if not success:
            raise HTTPException(
                status_code=404,
                detail=create_error_response(
                    errors=["User not found"]
                ).model_dump()
            )
        
        return create_success_response(
            data={"message": "User deleted successfully"}
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=create_error_response(
                errors=[f"Failed to delete user: {str(e)}"]
            ).model_dump()
        )



@router.post("/{user_id}/change-password", response_model=StandardAPIResponse)
async def change_password(
    user_id: int,
    password_data: UserPasswordChange,
    db: AsyncSession = Depends(get_db)
):
    """Change a user's password."""
    try:
        user_service = UserService(db)
        success = await user_service.change_password(user_id, password_data)
        
        if not success:
            raise HTTPException(
                status_code=400,
                detail=create_error_response(
                    errors=["Invalid current password or user not found"]
                ).model_dump()
            )
        
        return create_success_response(
            data={"message": "Password changed successfully"}
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=create_error_response(
                errors=[f"Failed to change password: {str(e)}"]
            ).model_dump()
        )


@router.post("/{user_id}/roles/{role}", response_model=StandardAPIResponse)
async def add_role_to_user(
    user_id: int,
    role: str,
    db: AsyncSession = Depends(get_db)
):
    """Add a role to a user."""
    try:
        user_service = UserService(db)
        user = await user_service.add_role_to_user(user_id, role)
        
        if not user:
            raise HTTPException(
                status_code=404,
                detail=create_error_response(
                    errors=["User not found"]
                ).model_dump()
            )
        
        return create_success_response(
            data=user
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=create_error_response(
                errors=[f"Failed to add role: {str(e)}"]
            ).model_dump()
        )


@router.delete("/{user_id}/roles/{role}", response_model=StandardAPIResponse)
async def remove_role_from_user(
    user_id: int,
    role: str,
    db: AsyncSession = Depends(get_db)
):
    """Remove a role from a user."""
    try:
        user_service = UserService(db)
        user = await user_service.remove_role_from_user(user_id, role)
        
        if not user:
            raise HTTPException(
                status_code=404,
                detail=create_error_response(
                    errors=["User not found"]
                ).model_dump()
            )
        
        return create_success_response(
            data=user
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=create_error_response(
                errors=[f"Failed to remove role: {str(e)}"]
            ).model_dump()
        )


@router.get("/by-role/{role}", response_model=StandardAPIResponse)
async def get_users_by_role(
    role: str,
    db: AsyncSession = Depends(get_db)
):
    """Get all users with a specific role."""
    try:
        user_service = UserService(db)
        users = await user_service.get_users_by_role(role)
        
        return create_success_response(
            data=users
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=create_error_response(
                errors=[f"Failed to get users by role: {str(e)}"]
            ).model_dump()
        )
