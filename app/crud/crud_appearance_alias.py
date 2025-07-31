from sqlalchemy.orm import Session

from app.models import AppearanceAlias
from app.schemas import AppearanceAliasCreate


def get_appearance_alias_by_alias_name(db: Session, appearance_id: int, alias_name: str):
    return db.query(AppearanceAlias).filter(AppearanceAlias.appearance_id == appearance_id,
                                            AppearanceAlias.alias_name == alias_name).first()


def create_appearance_alias(db: Session, appearance_alias: AppearanceAliasCreate):
    db_appearance_alias = AppearanceAlias(
        appearance_id=appearance_alias.appearance_id,
        alias_name=appearance_alias.alias_name
    )
    db.add(db_appearance_alias)
    db.commit()
    db.refresh(db_appearance_alias)
    return db_appearance_alias
