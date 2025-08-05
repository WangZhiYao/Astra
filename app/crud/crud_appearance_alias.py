from sqlalchemy.orm import Session

import app.models as models
import app.schemas as schemas
from app.core.operation_result import OperationResult, OperationStatus


def _get_appearance_alias_by_alias_name(db: Session, appearance_id: int, alias_name: str):
    return db.query(models.AppearanceAlias).filter(
        models.AppearanceAlias.appearance_id == appearance_id,
        models.AppearanceAlias.alias_name == alias_name
    ).first()


def create_appearance_alias(db: Session, appearance_alias: schemas.AppearanceAliasCreate):
    db_appearance_alias = _get_appearance_alias_by_alias_name(db=db,
                                                              appearance_id=appearance_alias.appearance_id,
                                                              alias_name=appearance_alias.alias_name)
    if db_appearance_alias:
        return OperationResult(status=OperationStatus.CONFLICT, data=db_appearance_alias)

    db_appearance_alias = models.AppearanceAlias(
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
        appearance_alias: schemas.AppearanceAliasUpdate
) -> OperationResult[schemas.AppearanceAlias]:
    db_appearance_alias = db.query(models.AppearanceAlias).filter(models.AppearanceAlias.id == alias_id).first()
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

    return OperationResult(
        status=OperationStatus.SUCCESS,
        data=schemas.AppearanceAlias.model_validate(db_appearance_alias)
    )


def delete_appearance_alias(db: Session, alias_id: int) -> OperationResult[schemas.AppearanceAlias]:
    db_appearance_alias = db.query(models.AppearanceAlias).filter(models.AppearanceAlias.id == alias_id).first()
    if not db_appearance_alias:
        return OperationResult(status=OperationStatus.NOT_FOUND)

    db.delete(db_appearance_alias)
    db.commit()

    return OperationResult(
        status=OperationStatus.SUCCESS,
        data=schemas.AppearanceAlias.model_validate(db_appearance_alias)
    )
