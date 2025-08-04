from sqlalchemy.orm import Session

from app.core.operation_result import OperationResult, OperationStatus
from app.models import AppearanceAlias
from app.schemas import AppearanceAliasCreate, AppearanceAliasUpdate


def _get_appearance_alias_by_alias_name(db: Session, appearance_id: int, alias_name: str):
    return db.query(AppearanceAlias).filter(
        AppearanceAlias.appearance_id == appearance_id,
        AppearanceAlias.alias_name == alias_name
    ).first()


def create_appearance_alias(db: Session, appearance_alias: AppearanceAliasCreate):
    db_appearance_alias = _get_appearance_alias_by_alias_name(db=db,
                                                              appearance_id=appearance_alias.appearance_id,
                                                              alias_name=appearance_alias.alias_name)
    if db_appearance_alias:
        return OperationResult(status=OperationStatus.CONFLICT, data=db_appearance_alias)

    db_appearance_alias = AppearanceAlias(
        appearance_id=appearance_alias.appearance_id,
        alias_name=appearance_alias.alias_name
    )
    db.add(db_appearance_alias)
    db.commit()
    db.refresh(db_appearance_alias)

    return OperationResult(status=OperationStatus.SUCCESS, data=db_appearance_alias)


def update_appearance_alias(
        db: Session,
        alias_id: int,
        appearance_alias: AppearanceAliasUpdate
) -> OperationResult[AppearanceAlias]:
    db_appearance_alias = db.query(AppearanceAlias).filter(AppearanceAlias.id == alias_id).first()
    if not db_appearance_alias:
        return OperationResult(status=OperationStatus.NOT_FOUND)

    update_data = appearance_alias.model_dump(exclude_unset=True)
    if "alias_name" in update_data and update_data["alias_name"] != db_appearance_alias.alias_name:
        existing_alias = _get_appearance_alias_by_alias_name(
            db=db,
            appearance_id=db_appearance_alias.appearance_id,
            alias_name=update_data["alias_name"]
        )
        if existing_alias:
            return OperationResult(status=OperationStatus.CONFLICT, data=existing_alias)

    for key, value in update_data.items():
        setattr(db_appearance_alias, key, value)
    db.add(db_appearance_alias)
    db.commit()
    db.refresh(db_appearance_alias)

    return OperationResult(status=OperationStatus.SUCCESS, data=db_appearance_alias)


def delete_appearance_alias(db: Session, alias_id: int):
    db_appearance_alias = db.query(AppearanceAlias).filter(AppearanceAlias.id == alias_id).first()
    if db_appearance_alias:
        db.delete(db_appearance_alias)
        db.commit()
    return db_appearance_alias
