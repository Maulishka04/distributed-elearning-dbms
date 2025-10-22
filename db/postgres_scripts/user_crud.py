"""
CRUD Operations for User Management
"""

from typing import Optional, Dict, List, Any
import uuid
from datetime import datetime
import hashlib
from .connection_manager import get_postgres_manager


class UserCRUD:
    """CRUD operations for users"""
    
    def __init__(self):
        self.pg_manager = get_postgres_manager()
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def create_user(
        self,
        email: str,
        password: str,
        first_name: str,
        last_name: str,
        user_type: str,
        region: str,
        country: Optional[str] = None,
        city: Optional[str] = None,
        phone: Optional[str] = None
    ) -> str:
        """
        Create a new user with profile
        
        Args:
            email: User email
            password: Plain text password (will be hashed)
            first_name: First name
            last_name: Last name
            user_type: Type of user (student, instructor, admin)
            region: Geographic region for sharding
            country: Country
            city: City
            phone: Phone number
        
        Returns:
            User ID (UUID as string)
        """
        password_hash = self.hash_password(password)
        
        result = self.pg_manager.call_procedure(
            region=region,
            procedure_name='create_user_with_profile',
            params=(email, password_hash, first_name, last_name, user_type, region, country, city, phone),
            read_only=False
        )
        
        # The procedure returns the user_id
        if result and len(result) > 0:
            return str(result[0]['create_user_with_profile'])
        
        raise Exception("Failed to create user")
    
    def get_user_by_id(self, user_id: str, region: str) -> Optional[Dict[str, Any]]:
        """Get user by ID"""
        query = """
            SELECT 
                u.user_id, u.email, u.first_name, u.last_name, u.user_type,
                u.region, u.status, u.created_at, u.last_login,
                up.country, up.city, up.phone_number, up.date_of_birth,
                up.bio, up.profile_picture_url, up.timezone, up.language_preference
            FROM users u
            LEFT JOIN user_profiles up ON u.user_id = up.user_id
            WHERE u.user_id = %s
        """
        
        result = self.pg_manager.execute_query(
            region=region,
            query=query,
            params=(user_id,),
            read_only=True,
            fetch_one=True
        )
        
        return result
    
    def get_user_by_email(self, email: str, region: str) -> Optional[Dict[str, Any]]:
        """Get user by email using stored procedure"""
        result = self.pg_manager.call_procedure(
            region=region,
            procedure_name='get_user_by_email',
            params=(email,),
            read_only=True
        )
        
        return result[0] if result else None
    
    def update_user(
        self,
        user_id: str,
        region: str,
        update_data: Dict[str, Any]
    ) -> bool:
        """Update user information"""
        # Build dynamic update query
        allowed_fields = ['first_name', 'last_name', 'status']
        updates = []
        params = []
        
        for field, value in update_data.items():
            if field in allowed_fields:
                updates.append(f"{field} = %s")
                params.append(value)
        
        if not updates:
            return False
        
        query = f"""
            UPDATE users
            SET {', '.join(updates)}, updated_at = CURRENT_TIMESTAMP
            WHERE user_id = %s
        """
        params.append(user_id)
        
        self.pg_manager.execute_query(
            region=region,
            query=query,
            params=tuple(params),
            read_only=False
        )
        
        return True
    
    def update_user_profile(
        self,
        user_id: str,
        region: str,
        profile_data: Dict[str, Any]
    ) -> bool:
        """Update user profile"""
        allowed_fields = [
            'phone_number', 'date_of_birth', 'country', 'city',
            'bio', 'profile_picture_url', 'timezone', 'language_preference'
        ]
        
        updates = []
        params = []
        
        for field, value in profile_data.items():
            if field in allowed_fields:
                updates.append(f"{field} = %s")
                params.append(value)
        
        if not updates:
            return False
        
        query = f"""
            UPDATE user_profiles
            SET {', '.join(updates)}, updated_at = CURRENT_TIMESTAMP
            WHERE user_id = %s
        """
        params.append(user_id)
        
        self.pg_manager.execute_query(
            region=region,
            query=query,
            params=tuple(params),
            read_only=False
        )
        
        return True
    
    def update_last_login(self, user_id: str, region: str) -> bool:
        """Update user's last login timestamp"""
        self.pg_manager.call_procedure(
            region=region,
            procedure_name='update_user_login',
            params=(user_id,),
            read_only=False
        )
        return True
    
    def delete_user(self, user_id: str, region: str) -> bool:
        """Delete user (soft delete by setting status to inactive)"""
        query = """
            UPDATE users
            SET status = 'inactive', updated_at = CURRENT_TIMESTAMP
            WHERE user_id = %s
        """
        
        self.pg_manager.execute_query(
            region=region,
            query=query,
            params=(user_id,),
            read_only=False
        )
        
        return True
    
    def list_users(
        self,
        region: str,
        user_type: Optional[str] = None,
        status: str = 'active',
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """List users with filters"""
        query = """
            SELECT 
                u.user_id, u.email, u.first_name, u.last_name,
                u.user_type, u.region, u.status, u.created_at
            FROM users u
            WHERE u.status = %s
        """
        params = [status]
        
        if user_type:
            query += " AND u.user_type = %s"
            params.append(user_type)
        
        query += " ORDER BY u.created_at DESC LIMIT %s OFFSET %s"
        params.extend([limit, offset])
        
        results = self.pg_manager.execute_query(
            region=region,
            query=query,
            params=tuple(params),
            read_only=True
        )
        
        return results or []
    
    def authenticate_user(self, email: str, password: str, region: str) -> Optional[Dict[str, Any]]:
        """Authenticate user with email and password"""
        password_hash = self.hash_password(password)
        
        query = """
            SELECT 
                u.user_id, u.email, u.first_name, u.last_name,
                u.user_type, u.region, u.status
            FROM users u
            WHERE u.email = %s AND u.password_hash = %s AND u.status = 'active'
        """
        
        result = self.pg_manager.execute_query(
            region=region,
            query=query,
            params=(email, password_hash),
            read_only=True,
            fetch_one=True
        )
        
        if result:
            # Update last login
            self.update_last_login(result['user_id'], region)
        
        return result
