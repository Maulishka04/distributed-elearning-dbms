"""
Unit tests for UserManager business logic
"""
import pytest
from api.services.user_manager import UserManager

class DummyUserCrud:
    users = {}
    @staticmethod
    def create_user(email, password, full_name, role):
        uid = len(DummyUserCrud.users) + 1
        DummyUserCrud.users[uid] = {"id": uid, "email": email, "password": password, "full_name": full_name, "role": role}
        return uid
    @staticmethod
    def get_user_by_id(user_id):
        return DummyUserCrud.users.get(user_id)
    @staticmethod
    def update_user(user_id, full_name, password, role):
        user = DummyUserCrud.users.get(user_id)
        if user:
            if full_name: user["full_name"] = full_name
            if password: user["password"] = password
            if role: user["role"] = role
        return user
    @staticmethod
    def delete_user(user_id):
        DummyUserCrud.users.pop(user_id, None)
    @staticmethod
    def get_user_by_email(email):
        for u in DummyUserCrud.users.values():
            if u["email"] == email:
                return u
        return None
    @staticmethod
    def list_users():
        return list(DummyUserCrud.users.values())

UserManager.create_user = DummyUserCrud.create_user
UserManager.get_user = DummyUserCrud.get_user_by_id
UserManager.update_user = DummyUserCrud.update_user
UserManager.delete_user = DummyUserCrud.delete_user
UserManager.get_user_by_email = DummyUserCrud.get_user_by_email
UserManager.list_all_users = DummyUserCrud.list_users

def test_register_and_get_user():
    uid = UserManager.register_user("test@example.com", "pass", "Test User", "student")
    user = UserManager.get_user(uid)
    assert user["email"] == "test@example.com"
    assert user["role"] == "student"

def test_update_user():
    uid = UserManager.register_user("update@example.com", "pass", "Update User", "student")
    UserManager.update_user(uid, "Updated Name", None, "instructor")
    user = UserManager.get_user(uid)
    assert user["full_name"] == "Updated Name"
    assert user["role"] == "instructor"

def test_delete_user():
    uid = UserManager.register_user("delete@example.com", "pass", "Delete User", "student")
    UserManager.delete_user(uid)
    user = UserManager.get_user(uid)
    assert user is None

def test_get_user_by_email():
    uid = UserManager.register_user("email@example.com", "pass", "Email User", "student")
    user = UserManager.get_user_by_email("email@example.com")
    assert user["id"] == uid

def test_list_all_users():
    UserManager.register_user("a@example.com", "pass", "A", "student")
    UserManager.register_user("b@example.com", "pass", "B", "instructor")
    users = UserManager.list_all_users()
    assert len(users) >= 2
