"""
Unit tests for AnalyticsManager business logic
"""
import pytest
from api.services.analytics_manager import AnalyticsManager

class DummyEnrollmentCrud:
    enrollments = [
        {"id": 1, "user_id": 1, "course_id": 1, "status": "active"},
        {"id": 2, "user_id": 2, "course_id": 1, "status": "active"},
        {"id": 3, "user_id": 1, "course_id": 2, "status": "active"}
    ]
    @staticmethod
    def list_enrollments():
        return DummyEnrollmentCrud.enrollments

class DummyPaymentCrud:
    payments = [
        {"id": 1, "user_id": 1, "enrollment_id": 1, "amount": 100.0, "status": "completed", "method": "card"},
        {"id": 2, "user_id": 2, "enrollment_id": 2, "amount": 200.0, "status": "completed", "method": "paypal"},
        {"id": 3, "user_id": 1, "enrollment_id": 3, "amount": 150.0, "status": "pending", "method": "card"}
    ]
    @staticmethod
    def list_payments():
        return DummyPaymentCrud.payments

AnalyticsManager.list_enrollments = DummyEnrollmentCrud.list_enrollments
AnalyticsManager.list_payments = DummyPaymentCrud.list_payments

AnalyticsManager.list_courses = lambda: [{"id": 1}, {"id": 2}]
AnalyticsManager.list_users = lambda: [{"id": 1}, {"id": 2}]
AnalyticsManager.get_mongo_collection = lambda name: None


def test_course_popularity():
    result = AnalyticsManager.course_popularity()
    assert any(r["course_id"] == 1 and r["enrollments"] == 2 for r in result)
    assert any(r["course_id"] == 2 and r["enrollments"] == 1 for r in result)

def test_financial_report():
    report = AnalyticsManager.financial_report()
    assert report["total_revenue"] == 300.0
    assert report["by_method"]["card"] == 100.0 + 150.0
    assert report["by_method"]["paypal"] == 200.0
