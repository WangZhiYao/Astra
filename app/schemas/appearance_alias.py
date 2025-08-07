from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class AppearanceAliasBase(BaseModel):
    appearance_id: int
    alias_name: str


class AppearanceAliasCreate(AppearanceAliasBase):
    pass


class AppearanceAliasUpdate(BaseModel):
    alias_name: Optional[str] = None


class AppearanceAlias(AppearanceAliasBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime


class AppearanceAliasSimple(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    alias_name: str
