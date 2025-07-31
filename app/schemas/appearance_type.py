from pydantic import BaseModel


class AppearanceTypeBase(BaseModel):
    name: str


class AppearanceTypeCreate(AppearanceTypeBase):
    pass


class AppearanceType(AppearanceTypeBase):
    id: int

    class Config:
        from_attributes = True
