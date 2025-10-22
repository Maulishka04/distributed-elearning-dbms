"""
Payment API Router for CRUD operations
"""

from fastapi import APIRouter, Depends, HTTPException, status
from api.schemas.payment import PaymentCreate, PaymentRead, PaymentUpdate
from api.services.payment_service import PaymentService
from api.utils.auth import get_current_user, TokenData

router = APIRouter()

@router.post("/", response_model=PaymentRead)
async def create_payment(payment: PaymentCreate, current_user: TokenData = Depends(get_current_user)):
    """Create a new payment."""
    return await PaymentService.create_payment(payment, current_user)

@router.get("/{payment_id}", response_model=PaymentRead)
async def get_payment(payment_id: int):
    """Get payment by ID."""
    return await PaymentService.get_payment(payment_id)

@router.put("/{payment_id}", response_model=PaymentRead)
async def update_payment(payment_id: int, payment: PaymentUpdate, current_user: TokenData = Depends(get_current_user)):
    """Update payment details."""
    return await PaymentService.update_payment(payment_id, payment, current_user)

@router.delete("/{payment_id}")
async def delete_payment(payment_id: int, current_user: TokenData = Depends(get_current_user)):
    """Delete payment by ID."""
    return await PaymentService.delete_payment(payment_id, current_user)
