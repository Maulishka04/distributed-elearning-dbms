"""
Business Logic for Course Management
Handles multimedia content and course CRUD.
"""

from typing import List, Dict, Optional
from db.postgres_scripts.course_crud import (
    create_course,
    get_course_by_id,
    update_course,
    delete_course,
    list_courses
)
from db.mongo_scripts.connection_manager import get_mongo_collection

class CourseManager:
    @staticmethod
    def create_course(title: str, description: str, instructor_id: int, category: str, price: float, multimedia: Optional[Dict] = None) -> int:
        course_id = create_course(title, description, instructor_id, category, price)
        if multimedia:
            collection = get_mongo_collection("course_content")
            collection.insert_one({"course_id": course_id, "content": multimedia})
        return course_id

    @staticmethod
    def get_course(course_id: int) -> Optional[Dict]:
        course = get_course_by_id(course_id)
        collection = get_mongo_collection("course_content")
        content = collection.find_one({"course_id": course_id})
        if course and content:
            course["multimedia"] = content["content"]
        return course

    @staticmethod
    def update_course(course_id: int, title: Optional[str], description: Optional[str], category: Optional[str], price: Optional[float], multimedia: Optional[Dict] = None) -> Dict:
        updated = update_course(course_id, title, description, category, price)
        if multimedia:
            collection = get_mongo_collection("course_content")
            collection.update_one({"course_id": course_id}, {"$set": {"content": multimedia}}, upsert=True)
        return updated

    @staticmethod
    def delete_course(course_id: int) -> None:
        delete_course(course_id)
        collection = get_mongo_collection("course_content")
        collection.delete_one({"course_id": course_id})

    @staticmethod
    def list_all_courses() -> List[Dict]:
        return list_courses()
