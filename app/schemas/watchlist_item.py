from typing import Optional

from pydantic import BaseModel


class WatchlistItemBase(BaseModel):
    appearance_id: int
    target_price_cents: Optional[int] = None
    notes: Optional[str] = None


class WatchlistItemCreate(WatchlistItemBase):
    pass


class WatchlistItem(WatchlistItemBase):
    id: int
    watchlist_id: int

    class Config:
        from_attributes = True
