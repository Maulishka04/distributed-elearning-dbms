"""
CRUD Operations for Course Management
"""

from typing import Optional, Dict, List, Any
import uuid
from datetime import datetime
from .connection_manager import get_postgres_manager


class CourseCRUD:
    """CRUD operations for courses"""
    
    def __init__(self):
        self.pg_manager = get_postgres_manager()
    
    def create_course(
        self,
        course_code: str,
        title: str,
        description: str,
        instructor_id: str,
        region: str,
        category_id: Optional[str] = None,
        level: str = 'beginner',
        price: float = 0.0,
        duration_hours: Optional[int] = None
    ) -> str:
        """Create a new course"""
        result = self.pg_manager.call_procedure(
            region=region,
            procedure_name='create_course',
            params=(course_code, title, description, instructor_id, 
                   category_id, level, price, duration_hours),
            read_only=False
        )
        
        if result and len(result) > 0:
            return str(result[0]['create_course'])
        
        raise Exception("Failed to create course")
    
    def get_course_by_id(self, course_id: str, region: str) -> Optional[Dict[str, Any]]:
        """Get detailed course information"""
        result = self.pg_manager.call_procedure(
            region=region,
            procedure_name='get_course_details',
            params=(course_id,),
            read_only=True
        )
        
        return result[0] if result else None
    
    def update_course(
        self,
        course_id: str,
        region: str,
        update_data: Dict[str, Any]
    ) -> bool:
        """Update course information"""
        allowed_fields = [
            'title', 'description', 'category_id', 'level',
            'price', 'duration_hours', 'language', 'status',
            'max_enrollments'
        ]
        
        updates = []
        params = []
        
        for field, value in update_data.items():
            if field in allowed_fields:
                updates.append(f"{field} = %s")
                params.append(value)
        
        if not updates:
            return False
        
        query = f"""
            UPDATE courses
            SET {', '.join(updates)}, updated_at = CURRENT_TIMESTAMP
            WHERE course_id = %s
        """
        params.append(course_id)
        
        self.pg_manager.execute_query(
            region=region,
            query=query,
            params=tuple(params),
            read_only=False
        )
        
        return True
    
    def publish_course(self, course_id: str, region: str) -> bool:
        """Publish a course"""
        query = """
            UPDATE courses
            SET status = 'published',
                published_at = CURRENT_TIMESTAMP,
                updated_at = CURRENT_TIMESTAMP
            WHERE course_id = %s AND status = 'draft'
        """
        
        self.pg_manager.execute_query(
            region=region,
            query=query,
            params=(course_id,),
            read_only=False
        )
        
        return True
    
    def archive_course(self, course_id: str, region: str) -> bool:
        """Archive a course"""
        query = """
            UPDATE courses
            SET status = 'archived', updated_at = CURRENT_TIMESTAMP
            WHERE course_id = %s
        """
        
        self.pg_manager.execute_query(
            region=region,
            query=query,
            params=(course_id,),
            read_only=False
        )
        
        return True
    
    def get_popular_courses(self, region: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get popular courses"""
        result = self.pg_manager.call_procedure(
            region=region,
            procedure_name='get_popular_courses',
            params=(limit,),
            read_only=True
        )
        
        return result or []
    
    def search_courses(
        self,
        region: str,
        search_term: Optional[str] = None,
        category_id: Optional[str] = None,
        min_rating: float = 0.0,
        max_price: Optional[float] = None
    ) -> List[Dict[str, Any]]:
        """Search courses with filters"""
        result = self.pg_manager.call_procedure(
            region=region,
            procedure_name='search_courses',
            params=(search_term, category_id, min_rating, max_price),
            read_only=True
        )
        
        return result or []
    
    def get_instructor_courses(
        self,
        instructor_id: str,
        region: str,
        status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get all courses by an instructor"""
        query = """
            SELECT 
                c.course_id, c.course_code, c.title, c.description,
                c.level, c.price, c.rating, c.total_ratings,
                c.status, c.created_at,
                COUNT(e.enrollment_id) as total_enrollments
            FROM courses c
            LEFT JOIN enrollments e ON c.course_id = e.course_id
            WHERE c.instructor_id = %s
        """
        params = [instructor_id]
        
        if status:
            query += " AND c.status = %s"
            params.append(status)
        
        query += " GROUP BY c.course_id ORDER BY c.created_at DESC"
        
        results = self.pg_manager.execute_query(
            region=region,
            query=query,
            params=tuple(params),
            read_only=True
        )
        
        return results or []
    
    def create_course_module(
        self,
        course_id: str,
        region: str,
        module_title: str,
        module_order: int,
        description: Optional[str] = None
    ) -> str:
        """Create a course module"""
        query = """
            INSERT INTO course_modules (course_id, module_title, module_order, description)
            VALUES (%s, %s, %s, %s)
            RETURNING module_id
        """
        
        result = self.pg_manager.execute_query(
            region=region,
            query=query,
            params=(course_id, module_title, module_order, description),
            read_only=False,
            fetch_one=True
        )
        
        return str(result['module_id']) if result else None
    
    def create_course_lesson(
        self,
        module_id: str,
        region: str,
        lesson_title: str,
        lesson_order: int,
        lesson_type: str,
        content_id: Optional[str] = None,
        duration_minutes: Optional[int] = None,
        is_preview: bool = False
    ) -> str:
        """Create a course lesson"""
        query = """
            INSERT INTO course_lessons 
            (module_id, lesson_title, lesson_order, lesson_type, content_id, duration_minutes, is_preview)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING lesson_id
        """
        
        result = self.pg_manager.execute_query(
            region=region,
            query=query,
            params=(module_id, lesson_title, lesson_order, lesson_type, 
                   content_id, duration_minutes, is_preview),
            read_only=False,
            fetch_one=True
        )
        
        return str(result['lesson_id']) if result else None
    
    def get_course_curriculum(self, course_id: str, region: str) -> List[Dict[str, Any]]:
        """Get complete course curriculum with modules and lessons"""
        query = """
            SELECT 
                cm.module_id, cm.module_title, cm.module_order, cm.description as module_description,
                cl.lesson_id, cl.lesson_title, cl.lesson_order, cl.lesson_type,
                cl.content_id, cl.duration_minutes, cl.is_preview
            FROM course_modules cm
            LEFT JOIN course_lessons cl ON cm.module_id = cl.module_id
            WHERE cm.course_id = %s
            ORDER BY cm.module_order, cl.lesson_order
        """
        
        results = self.pg_manager.execute_query(
            region=region,
            query=query,
            params=(course_id,),
            read_only=True
        )
        
        # Organize results into hierarchical structure
        curriculum = {}
        for row in results or []:
            module_id = str(row['module_id'])
            if module_id not in curriculum:
                curriculum[module_id] = {
                    'module_id': module_id,
                    'module_title': row['module_title'],
                    'module_order': row['module_order'],
                    'module_description': row['module_description'],
                    'lessons': []
                }
            
            if row['lesson_id']:
                curriculum[module_id]['lessons'].append({
                    'lesson_id': str(row['lesson_id']),
                    'lesson_title': row['lesson_title'],
                    'lesson_order': row['lesson_order'],
                    'lesson_type': row['lesson_type'],
                    'content_id': row['content_id'],
                    'duration_minutes': row['duration_minutes'],
                    'is_preview': row['is_preview']
                })
        
        return list(curriculum.values())
    
    def create_category(
        self,
        region: str,
        category_name: str,
        description: Optional[str] = None,
        parent_category_id: Optional[str] = None
    ) -> str:
        """Create a course category"""
        query = """
            INSERT INTO course_categories (category_name, description, parent_category_id)
            VALUES (%s, %s, %s)
            RETURNING category_id
        """
        
        result = self.pg_manager.execute_query(
            region=region,
            query=query,
            params=(category_name, description, parent_category_id),
            read_only=False,
            fetch_one=True
        )
        
        return str(result['category_id']) if result else None
    
    def get_all_categories(self, region: str) -> List[Dict[str, Any]]:
        """Get all course categories"""
        query = """
            SELECT category_id, category_name, description, parent_category_id, created_at
            FROM course_categories
            ORDER BY category_name
        """
        
        results = self.pg_manager.execute_query(
            region=region,
            query=query,
            read_only=True
        )
        
        return results or []
