from typing import Optional

from pydantic import BaseModel


class AppearanceTypeBase(BaseModel):
    name: str


class AppearanceTypeCreate(AppearanceTypeBase):
    pass


class AppearanceTypeUpdate(BaseModel):
    name: Optional[str] = None


class AppearanceType(AppearanceTypeBase):
    id: int

    class Config:
        from_attributes = True
