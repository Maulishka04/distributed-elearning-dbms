"""
Payment Service Layer for business logic and database integration
"""

from api.schemas.payment import PaymentCreate, PaymentRead, PaymentUpdate
from db.postgres_scripts.payment_crud import (
    create_payment,
    get_payment_by_id,
    update_payment,
    delete_payment
)
from fastapi import HTTPException, status

class PaymentService:
    @staticmethod
    async def create_payment(payment: PaymentCreate, current_user):
        payment_id = create_payment(payment.user_id, payment.enrollment_id, payment.amount, payment.status, payment.method)
        return PaymentRead(id=payment_id, **payment.dict())

    @staticmethod
    async def get_payment(payment_id: int) -> PaymentRead:
        db_payment = get_payment_by_id(payment_id)
        if not db_payment:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment not found")
        return PaymentRead(**db_payment)

    @staticmethod
    async def update_payment(payment_id: int, payment: PaymentUpdate, current_user) -> PaymentRead:
        db_payment = get_payment_by_id(payment_id)
        if not db_payment:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment not found")
        updated_payment = update_payment(payment_id, payment.status, payment.method)
        return PaymentRead(**updated_payment)

    @staticmethod
    async def delete_payment(payment_id: int, current_user):
        db_payment = get_payment_by_id(payment_id)
        if not db_payment:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment not found")
        delete_payment(payment_id)
        return {"detail": "Payment deleted"}
