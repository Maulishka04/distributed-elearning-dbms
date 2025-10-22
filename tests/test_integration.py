"""
Integration tests for FastAPI endpoints and business logic
"""
import pytest
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

def test_user_registration_and_login(sample_user):
    # Register user
    response = client.post("/api/v1/users/register", json=sample_user)
    assert response.status_code == 200
    user = response.json()
    assert user["email"] == sample_user["email"]
    # Login user
    response = client.post("/api/v1/users/login", json=sample_user)
    assert response.status_code == 200
    assert "access_token" in response.json()

# Add more integration tests for courses, enrollments, payments as implemented
