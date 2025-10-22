"""
Course Pydantic Schemas for API requests and responses
"""

from pydantic import BaseModel
from typing import Optional

class CourseCreate(BaseModel):
    title: str
    description: Optional[str] = None
    instructor_id: int
    category: Optional[str] = None
    price: Optional[float] = 0.0

class CourseRead(BaseModel):
    id: int
    title: str
    description: Optional[str]
    instructor_id: int
    category: Optional[str]
    price: float

class CourseUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    price: Optional[float] = None
