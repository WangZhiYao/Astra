from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict

from .platform import Platform


class PlatformPriceHistoryBase(BaseModel):
    appearance_id: int
    platform_id: int
    lowest_price_cents: int
    quantity_on_sale: Optional[int] = None
    recorded_at: datetime


class PlatformPriceHistoryCreate(PlatformPriceHistoryBase):
    pass


class PlatformPriceHistory(PlatformPriceHistoryBase):
    model_config = ConfigDict(from_attributes=True)

    id: int


class PlatformPriceHistoryPoint(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    platform: Platform
    lowest_price_cents: float
    quantity_on_sale: Optional[int] = None
    recorded_at: datetime
