from pydantic import BaseModel


class PlatformAppearanceRelationBase(BaseModel):
    platform_id: int
    appearance_id: int
    platform_appearance_id: str


class PlatformAppearanceRelationCreate(PlatformAppearanceRelationBase):
    pass


class PlatformAppearanceRelation(PlatformAppearanceRelationBase):
    class Config:
        from_attributes = True
