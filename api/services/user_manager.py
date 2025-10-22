"""
Business Logic for User Management
Handles students, instructors, administrators.
"""

from typing import List, Dict, Optional
from db.postgres_scripts.user_crud import (
    create_user,
    get_user_by_id,
    update_user,
    delete_user,
    get_user_by_email,
    list_users
)

class UserManager:
    @staticmethod
    def register_user(email: str, password: str, full_name: str, role: str) -> int:
        return create_user(email, password, full_name, role)

    @staticmethod
    def get_user(user_id: int) -> Optional[Dict]:
        return get_user_by_id(user_id)

    @staticmethod
    def update_user(user_id: int, full_name: Optional[str], password: Optional[str], role: Optional[str]) -> Dict:
        return update_user(user_id, full_name, password, role)

    @staticmethod
    def delete_user(user_id: int) -> None:
        delete_user(user_id)

    @staticmethod
    def get_user_by_email(email: str) -> Optional[Dict]:
        return get_user_by_email(email)

    @staticmethod
    def list_all_users() -> List[Dict]:
        return list_users()
