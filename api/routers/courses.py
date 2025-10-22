"""
Course API Router for CRUD operations
"""

from fastapi import APIRouter, Depends, HTTPException, status
from api.schemas.course import CourseCreate, CourseRead, CourseUpdate
from api.services.course_service import CourseService
from api.utils.auth import get_current_user, TokenData

router = APIRouter()

@router.post("/", response_model=CourseRead)
async def create_course(course: CourseCreate, current_user: TokenData = Depends(get_current_user)):
    """Create a new course."""
    return await CourseService.create_course(course, current_user)

@router.get("/{course_id}", response_model=CourseRead)
async def get_course(course_id: int):
    """Get course by ID."""
    return await CourseService.get_course(course_id)

@router.put("/{course_id}", response_model=CourseRead)
async def update_course(course_id: int, course: CourseUpdate, current_user: TokenData = Depends(get_current_user)):
    """Update course details."""
    return await CourseService.update_course(course_id, course, current_user)

@router.delete("/{course_id}")
async def delete_course(course_id: int, current_user: TokenData = Depends(get_current_user)):
    """Delete course by ID."""
    return await CourseService.delete_course(course_id, current_user)
