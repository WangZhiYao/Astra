from typing import Optional, List

from pydantic import BaseModel

from app.schemas import AppearanceAliasSimple, AppearanceType


class AppearanceCreate(BaseModel):
    name: str
    description: Optional[str] = None
    image_url: Optional[str] = None


class AppearanceUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    image_url: Optional[str] = None


class Appearance(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    image_url: Optional[str] = None
    appearance_aliases: List[AppearanceAliasSimple] = None
    appearance_types: List[AppearanceType] = None

    class Config:
        from_attributes = True
