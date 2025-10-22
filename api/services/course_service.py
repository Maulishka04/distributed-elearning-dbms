"""
Course Service Layer for business logic and database integration
"""

from api.schemas.course import CourseCreate, CourseRead, CourseUpdate
from db.postgres_scripts.course_crud import (
    create_course,
    get_course_by_id,
    update_course,
    delete_course
)
from fastapi import HTTPException, status

class CourseService:
    @staticmethod
    async def create_course(course: CourseCreate, current_user):
        course_id = create_course(course.title, course.description, course.instructor_id, course.category, course.price)
        return CourseRead(id=course_id, **course.dict())

    @staticmethod
    async def get_course(course_id: int) -> CourseRead:
        db_course = get_course_by_id(course_id)
        if not db_course:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
        return CourseRead(**db_course)

    @staticmethod
    async def update_course(course_id: int, course: CourseUpdate, current_user) -> CourseRead:
        db_course = get_course_by_id(course_id)
        if not db_course:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
        updated_course = update_course(course_id, course.title, course.description, course.category, course.price)
        return CourseRead(**updated_course)

    @staticmethod
    async def delete_course(course_id: int, current_user):
        db_course = get_course_by_id(course_id)
        if not db_course:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
        delete_course(course_id)
        return {"detail": "Course deleted"}
