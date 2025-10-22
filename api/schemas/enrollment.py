"""
Enrollment Pydantic Schemas for API requests and responses
"""

from pydantic import BaseModel
from typing import Optional

class EnrollmentCreate(BaseModel):
    user_id: int
    course_id: int
    status: Optional[str] = "active"

class EnrollmentRead(BaseModel):
    id: int
    user_id: int
    course_id: int
    status: str

class EnrollmentUpdate(BaseModel):
    status: Optional[str] = None
