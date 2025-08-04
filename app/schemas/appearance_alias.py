from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class AppearanceAliasBase(BaseModel):
    appearance_id: int
    alias_name: str


class AppearanceAliasCreate(AppearanceAliasBase):
    pass


class AppearanceAliasUpdate(BaseModel):
    alias_name: Optional[str] = None


class AppearanceAlias(AppearanceAliasBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AppearanceAliasSimple(BaseModel):
    id: int
    alias_name: str

    class Config:
        from_attributes = True
