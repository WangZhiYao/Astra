from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class UserPurchaseTransactionBase(BaseModel):
    appearance_id: int
    platform_id: Optional[int] = None
    quantity: int
    unit_price_cents: int
    purchased_at: datetime
    notes: Optional[str] = None


class UserPurchaseTransactionCreate(UserPurchaseTransactionBase):
    pass


class UserPurchaseTransactionUpdate(BaseModel):
    platform_id: Optional[int] = None
    quantity: Optional[int] = None
    unit_price_cents: Optional[int] = None
    purchased_at: Optional[datetime] = None
    notes: Optional[str] = None


class UserPurchaseTransaction(UserPurchaseTransactionBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    created_at: datetime
