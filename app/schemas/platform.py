from typing import Optional

from pydantic import BaseModel


class PlatformBase(BaseModel):
    name: str


class PlatformCreate(PlatformBase):
    pass


class PlatformUpdate(BaseModel):
    name: Optional[str] = None


class Platform(PlatformBase):
    id: int

    class Config:
        from_attributes = True
