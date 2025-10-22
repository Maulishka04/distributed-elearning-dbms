"""
User API Router for CRUD operations and authentication endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status
from api.schemas.user import UserCreate, UserRead, UserUpdate
from api.services.user_service import UserService
from api.utils.auth import get_current_user, TokenData

router = APIRouter()

@router.post("/register", response_model=UserRead)
async def register_user(user: UserCreate):
    """Register a new user."""
    return await UserService.register_user(user)

@router.post("/login")
async def login_user(user: UserCreate):
    """Authenticate user and return JWT token."""
    return await UserService.login_user(user)

@router.get("/{user_id}", response_model=UserRead)
async def get_user(user_id: int, current_user: TokenData = Depends(get_current_user)):
    """Get user by ID."""
    return await UserService.get_user(user_id)

@router.put("/{user_id}", response_model=UserRead)
async def update_user(user_id: int, user: UserUpdate, current_user: TokenData = Depends(get_current_user)):
    """Update user details."""
    return await UserService.update_user(user_id, user)

@router.delete("/{user_id}")
async def delete_user(user_id: int, current_user: TokenData = Depends(get_current_user)):
    """Delete user by ID."""
    return await UserService.delete_user(user_id)
