"""
Package initialization for database layer
"""

from .config.database_config import DatabaseConfig
from .postgres_scripts.connection_manager import (
    get_postgres_manager,
    close_postgres_connections
)
from .mongo_scripts.connection_manager import (
    get_mongo_manager,
    close_mongo_connection,
    CourseContentManager,
    UserPreferencesManager
)
from .postgres_scripts.user_crud import UserCRUD
from .postgres_scripts.course_crud import CourseCRUD
from .postgres_scripts.enrollment_crud import EnrollmentCRUD
from .postgres_scripts.payment_crud import PaymentCRUD

__all__ = [
    'DatabaseConfig',
    'get_postgres_manager',
    'close_postgres_connections',
    'get_mongo_manager',
    'close_mongo_connection',
    'CourseContentManager',
    'UserPreferencesManager',
    'UserCRUD',
    'CourseCRUD',
    'EnrollmentCRUD',
    'PaymentCRUD'
]
