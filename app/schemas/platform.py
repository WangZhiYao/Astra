from typing import Optional

from pydantic import BaseModel, ConfigDict


class PlatformBase(BaseModel):
    name: str


class PlatformCreate(PlatformBase):
    pass


class PlatformUpdate(BaseModel):
    name: Optional[str] = None


class Platform(PlatformBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
