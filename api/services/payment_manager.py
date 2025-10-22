"""
Business Logic for Payment Processing (Dummy Integration)
"""

from typing import List, Dict, Optional
from db.postgres_scripts.payment_crud import (
    create_payment,
    get_payment_by_id,
    update_payment,
    delete_payment,
    list_payments
)

class PaymentManager:
    @staticmethod
    def process_payment(user_id: int, enrollment_id: int, amount: float, method: str = "card", status: str = "pending") -> int:
        # Dummy integration: always succeed
        return create_payment(user_id, enrollment_id, amount, status, method)

    @staticmethod
    def get_payment(payment_id: int) -> Optional[Dict]:
        return get_payment_by_id(payment_id)

    @staticmethod
    def update_payment(payment_id: int, status: Optional[str] = None, method: Optional[str] = None) -> Dict:
        return update_payment(payment_id, status, method)

    @staticmethod
    def delete_payment(payment_id: int) -> None:
        delete_payment(payment_id)

    @staticmethod
    def list_all_payments() -> List[Dict]:
        return list_payments()
