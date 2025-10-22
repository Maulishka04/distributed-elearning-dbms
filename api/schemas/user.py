"""
User Pydantic Schemas for API requests and responses
"""

from pydantic import BaseModel, EmailStr
from typing import Optional

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = None
    role: Optional[str] = "student"

class UserRead(BaseModel):
    id: int
    email: EmailStr
    full_name: Optional[str]
    role: str

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    password: Optional[str] = None
    role: Optional[str] = None
