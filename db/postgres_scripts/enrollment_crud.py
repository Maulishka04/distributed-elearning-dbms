"""
CRUD Operations for Enrollment and Progress Tracking
"""

from typing import Optional, Dict, List, Any
from datetime import datetime
from .connection_manager import get_postgres_manager


class EnrollmentCRUD:
    """CRUD operations for enrollments and progress tracking"""
    
    def __init__(self):
        self.pg_manager = get_postgres_manager()
    
    def enroll_user(self, user_id: str, course_id: str, region: str) -> str:
        """Enroll a user in a course"""
        result = self.pg_manager.call_procedure(
            region=region,
            procedure_name='enroll_user',
            params=(user_id, course_id),
            read_only=False
        )
        
        if result and len(result) > 0:
            return str(result[0]['enroll_user'])
        
        raise Exception("Failed to enroll user")
    
    def get_user_enrollments(
        self,
        user_id: str,
        region: str,
        status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get all enrollments for a user"""
        result = self.pg_manager.call_procedure(
            region=region,
            procedure_name='get_user_enrollments',
            params=(user_id, status),
            read_only=True
        )
        
        return result or []
    
    def get_enrollment_by_id(
        self,
        enrollment_id: str,
        region: str
    ) -> Optional[Dict[str, Any]]:
        """Get enrollment details"""
        query = """
            SELECT 
                e.enrollment_id, e.user_id, e.course_id,
                e.enrollment_date, e.completion_date,
                e.progress_percentage, e.status,
                e.certificate_issued, e.certificate_url,
                e.last_accessed,
                c.title as course_title,
                u.first_name, u.last_name
            FROM enrollments e
            JOIN courses c ON e.course_id = c.course_id
            JOIN users u ON e.user_id = u.user_id
            WHERE e.enrollment_id = %s
        """
        
        result = self.pg_manager.execute_query(
            region=region,
            query=query,
            params=(enrollment_id,),
            read_only=True,
            fetch_one=True
        )
        
        return result
    
    def update_enrollment_status(
        self,
        enrollment_id: str,
        region: str,
        status: str
    ) -> bool:
        """Update enrollment status"""
        query = """
            UPDATE enrollments
            SET status = %s, updated_at = CURRENT_TIMESTAMP
            WHERE enrollment_id = %s
        """
        
        self.pg_manager.execute_query(
            region=region,
            query=query,
            params=(status, enrollment_id),
            read_only=False
        )
        
        return True
    
    def mark_lesson_complete(
        self,
        enrollment_id: str,
        lesson_id: str,
        region: str,
        time_spent: int = 0
    ) -> bool:
        """Mark a lesson as complete"""
        self.pg_manager.call_procedure(
            region=region,
            procedure_name='mark_lesson_complete',
            params=(enrollment_id, lesson_id, time_spent),
            read_only=False
        )
        
        return True
    
    def update_lesson_progress(
        self,
        enrollment_id: str,
        lesson_id: str,
        region: str,
        last_position: Optional[int] = None,
        time_spent: int = 0
    ) -> bool:
        """Update lesson progress without marking complete"""
        query = """
            UPDATE lesson_progress
            SET last_position = COALESCE(%s, last_position),
                time_spent_minutes = time_spent_minutes + %s,
                updated_at = CURRENT_TIMESTAMP
            WHERE enrollment_id = %s AND lesson_id = %s
        """
        
        self.pg_manager.execute_query(
            region=region,
            query=query,
            params=(last_position, time_spent, enrollment_id, lesson_id),
            read_only=False
        )
        
        return True
    
    def get_course_progress(
        self,
        enrollment_id: str,
        region: str
    ) -> List[Dict[str, Any]]:
        """Get detailed course progress"""
        result = self.pg_manager.call_procedure(
            region=region,
            procedure_name='get_course_progress',
            params=(enrollment_id,),
            read_only=True
        )
        
        return result or []
    
    def get_lesson_progress(
        self,
        enrollment_id: str,
        lesson_id: str,
        region: str
    ) -> Optional[Dict[str, Any]]:
        """Get progress for a specific lesson"""
        query = """
            SELECT 
                progress_id, enrollment_id, lesson_id,
                completed, completion_date,
                time_spent_minutes, last_position
            FROM lesson_progress
            WHERE enrollment_id = %s AND lesson_id = %s
        """
        
        result = self.pg_manager.execute_query(
            region=region,
            query=query,
            params=(enrollment_id, lesson_id),
            read_only=True,
            fetch_one=True
        )
        
        return result
    
    def add_course_review(
        self,
        enrollment_id: str,
        region: str,
        rating: int,
        review_text: Optional[str] = None
    ) -> str:
        """Add a course review"""
        query = """
            INSERT INTO course_reviews (enrollment_id, rating, review_text)
            VALUES (%s, %s, %s)
            ON CONFLICT (enrollment_id) 
            DO UPDATE SET rating = EXCLUDED.rating, 
                         review_text = EXCLUDED.review_text,
                         updated_at = CURRENT_TIMESTAMP
            RETURNING review_id
        """
        
        result = self.pg_manager.execute_query(
            region=region,
            query=query,
            params=(enrollment_id, rating, review_text),
            read_only=False,
            fetch_one=True
        )
        
        return str(result['review_id']) if result else None
    
    def get_course_reviews(
        self,
        course_id: str,
        region: str,
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Get reviews for a course"""
        query = """
            SELECT 
                cr.review_id, cr.rating, cr.review_text,
                cr.created_at, cr.updated_at,
                u.first_name, u.last_name,
                u.user_id
            FROM course_reviews cr
            JOIN enrollments e ON cr.enrollment_id = e.enrollment_id
            JOIN users u ON e.user_id = u.user_id
            WHERE e.course_id = %s
            ORDER BY cr.created_at DESC
            LIMIT %s OFFSET %s
        """
        
        results = self.pg_manager.execute_query(
            region=region,
            query=query,
            params=(course_id, limit, offset),
            read_only=True
        )
        
        return results or []
    
    def issue_certificate(
        self,
        enrollment_id: str,
        region: str,
        certificate_url: str
    ) -> bool:
        """Issue a certificate for completed course"""
        query = """
            UPDATE enrollments
            SET certificate_issued = TRUE,
                certificate_url = %s
            WHERE enrollment_id = %s 
            AND status = 'completed'
            AND progress_percentage >= 100
        """
        
        self.pg_manager.execute_query(
            region=region,
            query=query,
            params=(certificate_url, enrollment_id),
            read_only=False
        )
        
        return True
    
    def get_enrollment_statistics(
        self,
        course_id: str,
        region: str
    ) -> Dict[str, Any]:
        """Get enrollment statistics for a course"""
        query = """
            SELECT 
                COUNT(*) as total_enrollments,
                COUNT(CASE WHEN status = 'active' THEN 1 END) as active_enrollments,
                COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed_enrollments,
                COUNT(CASE WHEN status = 'dropped' THEN 1 END) as dropped_enrollments,
                AVG(progress_percentage) as average_progress,
                AVG(CASE WHEN completion_date IS NOT NULL 
                    THEN EXTRACT(DAY FROM (completion_date - enrollment_date)) 
                    END) as avg_completion_days
            FROM enrollments
            WHERE course_id = %s
        """
        
        result = self.pg_manager.execute_query(
            region=region,
            query=query,
            params=(course_id,),
            read_only=True,
            fetch_one=True
        )
        
        return result or {}
