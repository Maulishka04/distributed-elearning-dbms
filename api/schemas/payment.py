"""
Payment Pydantic Schemas for API requests and responses
"""

from pydantic import BaseModel
from typing import Optional

class PaymentCreate(BaseModel):
    user_id: int
    enrollment_id: int
    amount: float
    status: Optional[str] = "pending"
    method: Optional[str] = "card"

class PaymentRead(BaseModel):
    id: int
    user_id: int
    enrollment_id: int
    amount: float
    status: str
    method: str

class PaymentUpdate(BaseModel):
    status: Optional[str] = None
    method: Optional[str] = None
