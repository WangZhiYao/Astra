from typing import Optional, List

from pydantic import BaseModel

from .watchlist_item import WatchlistItem


class WatchlistBase(BaseModel):
    name: str
    description: Optional[str] = None


class WatchlistCreate(WatchlistBase):
    pass


class Watchlist(WatchlistBase):
    id: int
    user_id: int
    items: List[WatchlistItem] = []

    class Config:
        from_attributes = True
