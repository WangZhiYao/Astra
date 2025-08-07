from pydantic import BaseModel, ConfigDict


class PlatformAppearanceRelationBase(BaseModel):
    platform_id: int
    appearance_id: int
    platform_appearance_id: str


class PlatformAppearanceRelationCreate(PlatformAppearanceRelationBase):
    pass


class PlatformAppearanceRelation(PlatformAppearanceRelationBase):
    model_config = ConfigDict(from_attributes=True)
