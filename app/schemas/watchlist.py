from typing import Optional, List

from pydantic import BaseModel, ConfigDict

from .watchlist_item import WatchlistItem


class WatchlistBase(BaseModel):
    name: str
    description: Optional[str] = None


class WatchlistCreate(WatchlistBase):
    pass


class WatchlistUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


class Watchlist(WatchlistBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    items: List[WatchlistItem] = []
