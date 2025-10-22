"""
Business Logic for Enrollment Tracking and Progress Monitoring
"""

from typing import List, Dict, Optional
from db.postgres_scripts.enrollment_crud import (
    create_enrollment,
    get_enrollment_by_id,
    update_enrollment,
    delete_enrollment,
    list_enrollments
)
from db.mongo_scripts.connection_manager import get_mongo_collection

class EnrollmentManager:
    @staticmethod
    def enroll_user(user_id: int, course_id: int, status: str = "active") -> int:
        return create_enrollment(user_id, course_id, status)

    @staticmethod
    def get_enrollment(enrollment_id: int) -> Optional[Dict]:
        return get_enrollment_by_id(enrollment_id)

    @staticmethod
    def update_enrollment(enrollment_id: int, status: Optional[str] = None, progress: Optional[Dict] = None) -> Dict:
        updated = update_enrollment(enrollment_id, status)
        if progress:
            collection = get_mongo_collection("progress_tracking")
            collection.update_one({"enrollment_id": enrollment_id}, {"$set": {"progress": progress}}, upsert=True)
        return updated

    @staticmethod
    def delete_enrollment(enrollment_id: int) -> None:
        delete_enrollment(enrollment_id)
        collection = get_mongo_collection("progress_tracking")
        collection.delete_one({"enrollment_id": enrollment_id})

    @staticmethod
    def get_progress(enrollment_id: int) -> Optional[Dict]:
        collection = get_mongo_collection("progress_tracking")
        return collection.find_one({"enrollment_id": enrollment_id})

    @staticmethod
    def list_all_enrollments() -> List[Dict]:
        return list_enrollments()
