"""
Pytest fixtures for test data setup and teardown
"""
import pytest

@pytest.fixture(scope="session")
def test_db():
    # Setup: create in-memory test DB or mock DB connection
    db = {}
    yield db
    # Teardown: clean up resources
    db.clear()

@pytest.fixture(scope="function")
def sample_user():
    return {"email": "testuser@example.com", "password": "testpass", "full_name": "Test User", "role": "student"}

@pytest.fixture(scope="function")
def sample_course():
    return {"title": "Test Course", "description": "A course for testing", "instructor_id": 1, "category": "Test", "price": 0.0}

@pytest.fixture(scope="function")
def sample_enrollment():
    return {"user_id": 1, "course_id": 1, "status": "active"}

@pytest.fixture(scope="function")
def sample_payment():
    return {"user_id": 1, "enrollment_id": 1, "amount": 100.0, "status": "completed", "method": "card"}
