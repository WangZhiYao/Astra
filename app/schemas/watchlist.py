from typing import Optional

from pydantic import BaseModel, ConfigDict


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
