from typing import Optional, List

from pydantic import BaseModel, ConfigDict

from .appearance_alias import AppearanceAliasSimple
from .appearance_type import AppearanceType


class AppearanceCreate(BaseModel):
    name: str
    description: Optional[str] = None
    image_url: Optional[str] = None


class AppearanceUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    image_url: Optional[str] = None


class Appearance(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: Optional[str] = None
    image_url: Optional[str] = None
    appearance_aliases: List[AppearanceAliasSimple] = None
    appearance_types: List[AppearanceType] = None
