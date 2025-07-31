from pydantic import BaseModel


class PlatformBase(BaseModel):
    name: str


class PlatformCreate(PlatformBase):
    pass


class Platform(PlatformBase):
    id: int

    class Config:
        from_attributes = True
