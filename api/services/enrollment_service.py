"""
Enrollment Service Layer for business logic and database integration
"""

from api.schemas.enrollment import EnrollmentCreate, EnrollmentRead, EnrollmentUpdate
from db.postgres_scripts.enrollment_crud import (
    create_enrollment,
    get_enrollment_by_id,
    update_enrollment,
    delete_enrollment
)
from fastapi import HTTPException, status

class EnrollmentService:
    @staticmethod
    async def create_enrollment(enrollment: EnrollmentCreate, current_user):
        enrollment_id = create_enrollment(enrollment.user_id, enrollment.course_id, enrollment.status)
        return EnrollmentRead(id=enrollment_id, **enrollment.dict())

    @staticmethod
    async def get_enrollment(enrollment_id: int) -> EnrollmentRead:
        db_enrollment = get_enrollment_by_id(enrollment_id)
        if not db_enrollment:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Enrollment not found")
        return EnrollmentRead(**db_enrollment)

    @staticmethod
    async def update_enrollment(enrollment_id: int, enrollment: EnrollmentUpdate, current_user) -> EnrollmentRead:
        db_enrollment = get_enrollment_by_id(enrollment_id)
        if not db_enrollment:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Enrollment not found")
        updated_enrollment = update_enrollment(enrollment_id, enrollment.status)
        return EnrollmentRead(**updated_enrollment)

    @staticmethod
    async def delete_enrollment(enrollment_id: int, current_user):
        db_enrollment = get_enrollment_by_id(enrollment_id)
        if not db_enrollment:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Enrollment not found")
        delete_enrollment(enrollment_id)
        return {"detail": "Enrollment deleted"}
