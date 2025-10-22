"""
Authentication Router for login and registration endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status
from api.schemas.user import UserCreate, UserRead
from api.services.user_service import UserService
from api.utils.auth import get_current_user, TokenData

router = APIRouter()

@router.post("/register", response_model=UserRead)
async def register(user: UserCreate):
    """Register a new user."""
    return await UserService.register_user(user)

@router.post("/login")
async def login(user: UserCreate):
    """Authenticate user and return JWT token."""
    return await UserService.login_user(user)
