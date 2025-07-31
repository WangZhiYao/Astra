from typing import Optional

from pydantic import BaseModel


class AppearanceCreate(BaseModel):
    name: str
    description: Optional[str] = None
    image_url: Optional[str] = None


class Appearance(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    image_url: Optional[str] = None

    class Config:
        from_attributes = True
