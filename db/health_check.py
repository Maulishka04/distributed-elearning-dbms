"""
Database Health Check and Monitoring Utility
"""

import sys
import os
from datetime import datetime
from typing import Dict, Any

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from db.postgres_scripts.connection_manager import get_postgres_manager
from db.mongo_scripts.connection_manager import get_mongo_manager


class DatabaseHealthCheck:
    """Monitor database health and connectivity"""
    
    def __init__(self):
        self.pg_manager = get_postgres_manager()
        self.mongo_manager = get_mongo_manager()
    
    def check_postgres_health(self) -> Dict[str, Any]:
        """Check PostgreSQL cluster health"""
        print("\nChecking PostgreSQL Health...")
        print("-" * 60)
        
        health_status = self.pg_manager.health_check()
        
        total_nodes = len(health_status)
        healthy_nodes = sum(1 for status in health_status.values() if status)
        
        for node, is_healthy in health_status.items():
            status_symbol = "✓" if is_healthy else "✗"
            print(f"  {status_symbol} {node}: {'HEALTHY' if is_healthy else 'UNHEALTHY'}")
        
        print(f"\nPostgreSQL Summary: {healthy_nodes}/{total_nodes} nodes healthy")
        
        return {
            'total_nodes': total_nodes,
            'healthy_nodes': healthy_nodes,
            'all_healthy': healthy_nodes == total_nodes,
            'details': health_status
        }
    
    def check_mongodb_health(self) -> Dict[str, bool]:
        """Check MongoDB health"""
        print("\nChecking MongoDB Health...")
        print("-" * 60)
        
        is_healthy = self.mongo_manager.health_check()
        status_symbol = "✓" if is_healthy else "✗"
        
        print(f"  {status_symbol} MongoDB: {'HEALTHY' if is_healthy else 'UNHEALTHY'}")
        
        return {
            'healthy': is_healthy
        }
    
    def get_database_stats(self):
        """Get database statistics"""
        print("\nDatabase Statistics...")
        print("-" * 60)
        
        try:
            # Get stats from one region (north_america)
            region = 'north_america'
            
            # Platform statistics
            query = "SELECT * FROM get_platform_stats()"
            result = self.pg_manager.execute_query(
                region=region,
                query=query,
                read_only=True,
                fetch_one=True
            )
            
            if result:
                print(f"\nPlatform Statistics:")
                print(f"  Total Users: {result.get('total_users', 0)}")
                print(f"  Students: {result.get('total_students', 0)}")
                print(f"  Instructors: {result.get('total_instructors', 0)}")
                print(f"  Total Courses: {result.get('total_courses', 0)}")
                print(f"  Published Courses: {result.get('published_courses', 0)}")
                print(f"  Total Enrollments: {result.get('total_enrollments', 0)}")
                print(f"  Active Enrollments: {result.get('active_enrollments', 0)}")
                print(f"  Total Revenue: ${result.get('total_revenue', 0) or 0:,.2f}")
            
            # MongoDB statistics
            db = self.mongo_manager.db
            content_count = db.course_content.count_documents({})
            preferences_count = db.user_preferences.count_documents({})
            
            print(f"\nMongoDB Statistics:")
            print(f"  Course Content Documents: {content_count}")
            print(f"  User Preferences Documents: {preferences_count}")
            
        except Exception as e:
            print(f"  Error getting statistics: {e}")
    
    def run_full_check(self):
        """Run comprehensive health check"""
        print("\n" + "="*60)
        print("E-Learning Platform - Database Health Check")
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*60)
        
        try:
            pg_health = self.check_postgres_health()
            mongo_health = self.check_mongodb_health()
            
            self.get_database_stats()
            
            print("\n" + "="*60)
            if pg_health['all_healthy'] and mongo_health['healthy']:
                print("✓ All database systems are healthy!")
            else:
                print("✗ Some database systems are unhealthy. Check logs above.")
            print("="*60 + "\n")
            
        except Exception as e:
            print(f"\n✗ Error during health check: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    health_check = DatabaseHealthCheck()
    health_check.run_full_check()
