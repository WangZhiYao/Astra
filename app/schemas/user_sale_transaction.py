from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


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


class UserSaleTransactionUpdate(BaseModel):
    platform_id: Optional[int] = None
    quantity: Optional[int] = None
    unit_price_cents: Optional[int] = None
    platform_fee_cents: Optional[int] = None
    sold_at: Optional[datetime] = None
    notes: Optional[str] = None


class UserSaleTransaction(UserSaleTransactionBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    created_at: datetime
