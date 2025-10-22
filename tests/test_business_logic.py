"""
Unit tests for business logic functions
"""
import pytest
from api.services.analytics_manager import AnalyticsManager

# Dummy data for analytics tests
def test_course_popularity():
    result = AnalyticsManager.course_popularity()
    assert isinstance(result, list)
    assert all("course_id" in r and "enrollments" in r for r in result)

def test_financial_report():
    report = AnalyticsManager.financial_report()
    assert "total_revenue" in report
    assert "by_method" in report
