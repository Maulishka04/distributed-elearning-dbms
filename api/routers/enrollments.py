"""
Enrollment API Router for CRUD operations
"""

from fastapi import APIRouter, Depends, HTTPException, status
from api.schemas.enrollment import EnrollmentCreate, EnrollmentRead, EnrollmentUpdate
from api.services.enrollment_service import EnrollmentService
from api.utils.auth import get_current_user, TokenData

router = APIRouter()

@router.post("/", response_model=EnrollmentRead)
async def create_enrollment(enrollment: EnrollmentCreate, current_user: TokenData = Depends(get_current_user)):
    """Enroll a user in a course."""
    return await EnrollmentService.create_enrollment(enrollment, current_user)

@router.get("/{enrollment_id}", response_model=EnrollmentRead)
async def get_enrollment(enrollment_id: int):
    """Get enrollment by ID."""
    return await EnrollmentService.get_enrollment(enrollment_id)

@router.put("/{enrollment_id}", response_model=EnrollmentRead)
async def update_enrollment(enrollment_id: int, enrollment: EnrollmentUpdate, current_user: TokenData = Depends(get_current_user)):
    """Update enrollment details."""
    return await EnrollmentService.update_enrollment(enrollment_id, enrollment, current_user)

@router.delete("/{enrollment_id}")
async def delete_enrollment(enrollment_id: int, current_user: TokenData = Depends(get_current_user)):
    """Delete enrollment by ID."""
    return await EnrollmentService.delete_enrollment(enrollment_id, current_user)
