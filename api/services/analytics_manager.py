"""
Business Logic for Analytics Functions
Course popularity, user progress, financial reporting.
"""

from typing import List, Dict
from db.postgres_scripts.course_crud import list_courses
from db.postgres_scripts.enrollment_crud import list_enrollments
from db.postgres_scripts.payment_crud import list_payments
from db.postgres_scripts.user_crud import list_users
from db.mongo_scripts.connection_manager import get_mongo_collection

class AnalyticsManager:
    @staticmethod
    def course_popularity() -> List[Dict]:
        enrollments = list_enrollments()
        popularity = {}
        for e in enrollments:
            cid = e["course_id"]
            popularity[cid] = popularity.get(cid, 0) + 1
        return [{"course_id": k, "enrollments": v} for k, v in popularity.items()]

    @staticmethod
    def user_progress(user_id: int) -> List[Dict]:
        enrollments = [e for e in list_enrollments() if e["user_id"] == user_id]
        collection = get_mongo_collection("progress_tracking")
        progress = []
        for e in enrollments:
            p = collection.find_one({"enrollment_id": e["id"]})
            progress.append({"enrollment_id": e["id"], "progress": p["progress"] if p else None})
        return progress

    @staticmethod
    def financial_report() -> Dict:
        payments = list_payments()
        total = sum(p["amount"] for p in payments if p["status"] == "completed")
        by_method = {}
        for p in payments:
            m = p["method"]
            by_method[m] = by_method.get(m, 0) + p["amount"]
        return {"total_revenue": total, "by_method": by_method}
