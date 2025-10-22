"""
User Service Layer for business logic and database integration
"""

from api.schemas.user import UserCreate, UserRead, UserUpdate
from api.utils.auth import create_access_token
from db.postgres_scripts.user_crud import (
    create_user,
    get_user_by_id,
    update_user,
    delete_user,
    get_user_by_email
)
from fastapi import HTTPException, status
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserService:
    @staticmethod
    async def register_user(user: UserCreate) -> UserRead:
        if get_user_by_email(user.email):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
        hashed_password = pwd_context.hash(user.password)
        user_id = create_user(user.email, hashed_password, user.full_name, user.role)
        return UserRead(id=user_id, email=user.email, full_name=user.full_name, role=user.role)

    @staticmethod
    async def login_user(user: UserCreate):
        db_user = get_user_by_email(user.email)
        if not db_user or not pwd_context.verify(user.password, db_user["password"]):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
        token = create_access_token({"user_id": db_user["id"], "email": db_user["email"], "role": db_user["role"]})
        return {"access_token": token, "token_type": "bearer"}

    @staticmethod
    async def get_user(user_id: int) -> UserRead:
        db_user = get_user_by_id(user_id)
        if not db_user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return UserRead(**db_user)

    @staticmethod
    async def update_user(user_id: int, user: UserUpdate) -> UserRead:
        db_user = get_user_by_id(user_id)
        if not db_user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        updated_user = update_user(user_id, user.full_name, user.password, user.role)
        return UserRead(**updated_user)

    @staticmethod
    async def delete_user(user_id: int):
        db_user = get_user_by_id(user_id)
        if not db_user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        delete_user(user_id)
        return {"detail": "User deleted"}
