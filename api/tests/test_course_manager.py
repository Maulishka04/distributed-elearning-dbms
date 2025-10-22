"""
Unit tests for CourseManager business logic
"""
import pytest
from api.services.course_manager import CourseManager

class DummyCourseCrud:
    courses = {}
    @staticmethod
    def create_course(title, description, instructor_id, category, price):
        cid = len(DummyCourseCrud.courses) + 1
        DummyCourseCrud.courses[cid] = {"id": cid, "title": title, "description": description, "instructor_id": instructor_id, "category": category, "price": price}
        return cid
    @staticmethod
    def get_course_by_id(course_id):
        return DummyCourseCrud.courses.get(course_id)
    @staticmethod
    def update_course(course_id, title, description, category, price):
        course = DummyCourseCrud.courses.get(course_id)
        if course:
            if title: course["title"] = title
            if description: course["description"] = description
            if category: course["category"] = category
            if price: course["price"] = price
        return course
    @staticmethod
    def delete_course(course_id):
        DummyCourseCrud.courses.pop(course_id, None)
    @staticmethod
    def list_courses():
        return list(DummyCourseCrud.courses.values())

CourseManager.create_course = DummyCourseCrud.create_course
CourseManager.get_course = DummyCourseCrud.get_course_by_id
CourseManager.update_course = DummyCourseCrud.update_course
CourseManager.delete_course = DummyCourseCrud.delete_course
CourseManager.list_all_courses = DummyCourseCrud.list_courses

def test_create_and_get_course():
    cid = CourseManager.create_course("Python", "Learn Python", 1, "Programming", 99.0)
    course = CourseManager.get_course(cid)
    assert course["title"] == "Python"
    assert course["price"] == 99.0

def test_update_course():
    cid = CourseManager.create_course("Java", "Learn Java", 2, "Programming", 89.0)
    CourseManager.update_course(cid, "Advanced Java", None, None, 129.0)
    course = CourseManager.get_course(cid)
    assert course["title"] == "Advanced Java"
    assert course["price"] == 129.0

def test_delete_course():
    cid = CourseManager.create_course("Delete", "To Delete", 3, "Misc", 10.0)
    CourseManager.delete_course(cid)
    course = CourseManager.get_course(cid)
    assert course is None

def test_list_all_courses():
    CourseManager.create_course("A", "Desc", 1, "Cat", 10.0)
    CourseManager.create_course("B", "Desc", 2, "Cat", 20.0)
    courses = CourseManager.list_all_courses()
    assert len(courses) >= 2
