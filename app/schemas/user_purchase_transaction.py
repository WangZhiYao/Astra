from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class UserPurchaseTransactionBase(BaseModel):
    appearance_id: int
    platform_id: Optional[int] = None
    quantity: int
    unit_price_cents: int
    purchased_at: datetime
    notes: Optional[str] = None


class UserPurchaseTransactionCreate(UserPurchaseTransactionBase):
    pass


class UserPurchaseTransaction(UserPurchaseTransactionBase):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True
