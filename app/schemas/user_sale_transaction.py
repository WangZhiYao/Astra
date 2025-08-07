from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict

from .appearance import Appearance
from .platform import Platform


class UserSaleTransactionBase(BaseModel):
    quantity: int
    unit_price_cents: int
    platform_fee_cents: int = 0
    sold_at: datetime
    notes: Optional[str] = None


class UserSaleTransactionCreate(UserSaleTransactionBase):
    appearance_id: int
    platform_id: Optional[int] = None


class UserSaleTransactionUpdate(UserSaleTransactionCreate):
    pass


class UserSaleTransaction(UserSaleTransactionBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    appearance: Appearance
    platform: Optional[Platform] = None
    created_at: datetime
