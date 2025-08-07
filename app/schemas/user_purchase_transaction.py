from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict

from .appearance import Appearance
from .platform import Platform


class UserPurchaseTransactionBase(BaseModel):
    quantity: int
    unit_price_cents: int
    purchased_at: datetime
    notes: Optional[str] = None


class UserPurchaseTransactionCreate(UserPurchaseTransactionBase):
    appearance_id: int
    platform_id: Optional[int] = None


class UserPurchaseTransactionUpdate(UserPurchaseTransactionCreate):
    pass


class UserPurchaseTransaction(UserPurchaseTransactionBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    appearance: Appearance
    platform: Optional[Platform] = None
    created_at: datetime
