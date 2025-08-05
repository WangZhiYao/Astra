from typing import Optional

from pydantic import BaseModel, ConfigDict


class AppearanceTypeBase(BaseModel):
    name: str


class AppearanceTypeCreate(AppearanceTypeBase):
    pass


class AppearanceTypeUpdate(BaseModel):
    name: Optional[str] = None


class AppearanceType(AppearanceTypeBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
