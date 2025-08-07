from typing import Optional

from pydantic import BaseModel, ConfigDict

from .appearance import Appearance


class WatchlistItemBase(BaseModel):
    appearance_id: int
    target_price_cents: Optional[int] = None
    notes: Optional[str] = None


class WatchlistItemCreate(WatchlistItemBase):
    pass


class WatchlistItem(WatchlistItemBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    watchlist_id: int
    appearance: Optional[Appearance] = None
