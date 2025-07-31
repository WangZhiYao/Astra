from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class UserSaleTransactionBase(BaseModel):
    appearance_id: int
    platform_id: Optional[int] = None
    quantity: int
    unit_price_cents: int
    platform_fee_cents: int = 0
    sold_at: datetime
    notes: Optional[str] = None


class UserSaleTransactionCreate(UserSaleTransactionBase):
    pass


class UserSaleTransaction(UserSaleTransactionBase):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True
