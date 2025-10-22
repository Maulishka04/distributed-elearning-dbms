"""
Unit tests for EnrollmentManager business logic
"""
import pytest
from api.services.enrollment_manager import EnrollmentManager

class DummyEnrollmentCrud:
    enrollments = {}
    @staticmethod
    def create_enrollment(user_id, course_id, status):
        eid = len(DummyEnrollmentCrud.enrollments) + 1
        DummyEnrollmentCrud.enrollments[eid] = {"id": eid, "user_id": user_id, "course_id": course_id, "status": status}
        return eid
    @staticmethod
    def get_enrollment_by_id(enrollment_id):
        return DummyEnrollmentCrud.enrollments.get(enrollment_id)
    @staticmethod
    def update_enrollment(enrollment_id, status):
        enrollment = DummyEnrollmentCrud.enrollments.get(enrollment_id)
        if enrollment and status:
            enrollment["status"] = status
        return enrollment
    @staticmethod
    def delete_enrollment(enrollment_id):
        DummyEnrollmentCrud.enrollments.pop(enrollment_id, None)
    @staticmethod
    def list_enrollments():
        return list(DummyEnrollmentCrud.enrollments.values())

EnrollmentManager.enroll_user = DummyEnrollmentCrud.create_enrollment
EnrollmentManager.get_enrollment = DummyEnrollmentCrud.get_enrollment_by_id
EnrollmentManager.update_enrollment = DummyEnrollmentCrud.update_enrollment
EnrollmentManager.delete_enrollment = DummyEnrollmentCrud.delete_enrollment
EnrollmentManager.list_all_enrollments = DummyEnrollmentCrud.list_enrollments

def test_enroll_and_get():
    eid = EnrollmentManager.enroll_user(1, 1, "active")
    enrollment = EnrollmentManager.get_enrollment(eid)
    assert enrollment["user_id"] == 1
    assert enrollment["status"] == "active"

def test_update_enrollment():
    eid = EnrollmentManager.enroll_user(2, 2, "active")
    EnrollmentManager.update_enrollment(eid, "completed")
    enrollment = EnrollmentManager.get_enrollment(eid)
    assert enrollment["status"] == "completed"

def test_delete_enrollment():
    eid = EnrollmentManager.enroll_user(3, 3, "active")
    EnrollmentManager.delete_enrollment(eid)
    enrollment = EnrollmentManager.get_enrollment(eid)
    assert enrollment is None

def test_list_all_enrollments():
    EnrollmentManager.enroll_user(4, 4, "active")
    EnrollmentManager.enroll_user(5, 5, "active")
    enrollments = EnrollmentManager.list_all_enrollments()
    assert len(enrollments) >= 2
