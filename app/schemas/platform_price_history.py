from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class PlatformPriceHistoryBase(BaseModel):
    appearance_id: int
    platform_id: int
    lowest_price_cents: int
    quantity_on_sale: Optional[int] = None
    crawled_at: datetime


class PlatformPriceHistoryCreate(PlatformPriceHistoryBase):
    pass


class PlatformPriceHistory(PlatformPriceHistoryBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
