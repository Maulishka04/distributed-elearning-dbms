"""
Unit tests for database CRUD operations (mocked)
"""
import pytest
from api.services.user_manager import UserManager
from api.services.course_manager import CourseManager
from api.services.enrollment_manager import EnrollmentManager
from api.services.payment_manager import PaymentManager

# Use dummy CRUD logic for isolated tests
def test_user_crud(sample_user):
    uid = UserManager.register_user(**sample_user)
    user = UserManager.get_user(uid)
    assert user["email"] == sample_user["email"]
    UserManager.delete_user(uid)
    assert UserManager.get_user(uid) is None

def test_course_crud(sample_course):
    cid = CourseManager.create_course(**sample_course)
    course = CourseManager.get_course(cid)
    assert course["title"] == sample_course["title"]
    CourseManager.delete_course(cid)
    assert CourseManager.get_course(cid) is None

def test_enrollment_crud(sample_enrollment):
    eid = EnrollmentManager.enroll_user(**sample_enrollment)
    enrollment = EnrollmentManager.get_enrollment(eid)
    assert enrollment["user_id"] == sample_enrollment["user_id"]
    EnrollmentManager.delete_enrollment(eid)
    assert EnrollmentManager.get_enrollment(eid) is None

def test_payment_crud(sample_payment):
    pid = PaymentManager.process_payment(**sample_payment)
    payment = PaymentManager.get_payment(pid)
    assert payment["amount"] == sample_payment["amount"]
    PaymentManager.delete_payment(pid)
    assert PaymentManager.get_payment(pid) is None
