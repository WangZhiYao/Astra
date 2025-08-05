from typing import List, Optional

from sqlalchemy.orm import Session
from sqlalchemy.orm import joinedload

import app.models as models
import app.schemas as schemas
from app.core.operation_result import OperationResult, OperationStatus


def _get_appearance_by_name(db: Session, name: str) -> Optional[models.Appearance]:
    return db.query(models.Appearance).filter(models.Appearance.name == name).first()


def create_appearance(db: Session, appearance: schemas.AppearanceCreate):
    db_appearance = _get_appearance_by_name(db=db, name=appearance.name)
    if db_appearance:
        return OperationResult(status=OperationStatus.CONFLICT, data=db_appearance)

    db_appearance = models.Appearance(
        name=appearance.name,
        description=appearance.description,
        image_url=appearance.image_url
    )

    db.add(db_appearance)
    db.commit()
    db.refresh(db_appearance)

    return OperationResult(status=OperationStatus.SUCCESS, data=schemas.Appearance.model_validate(db_appearance))


def get_appearance_by_id(db: Session, appearance_id: int):
    db_appearance = db.query(models.Appearance).options(
        joinedload(models.Appearance.appearance_aliases),
        joinedload(models.Appearance.appearance_types)
    ).filter(models.Appearance.id == appearance_id).first()

    if not db_appearance:
        return OperationResult(status=OperationStatus.NOT_FOUND)

    return OperationResult(status=OperationStatus.SUCCESS, data=schemas.Appearance.model_validate(db_appearance))


def get_appearances(
        db: Session,
        page: int = 1,
        page_size: int = 100,
        search_query: Optional[str] = None
) -> List[schemas.Appearance]:
    query = db.query(models.Appearance).options(
        joinedload(models.Appearance.appearance_aliases),
        joinedload(models.Appearance.appearance_types)
    )

    if search_query:
        query = query.outerjoin(models.Appearance.appearance_aliases).filter(
            (models.Appearance.name.ilike(f"%{search_query}%")) |
            (models.Appearance.appearance_aliases.any(models.AppearanceAlias.alias_name.ilike(f"%{search_query}%")))
        )

    offset = (page - 1) * page_size
    return query.offset(offset).limit(page_size).all()


def update_appearance(
        db: Session,
        appearance_id: int,
        appearance: schemas.AppearanceUpdate
) -> OperationResult[schemas.Appearance]:
    db_appearance = db.query(models.Appearance).filter(models.Appearance.id == appearance_id).first()
    if not db_appearance:
        return OperationResult(status=OperationStatus.NOT_FOUND)

    update_data = appearance.model_dump(exclude_unset=True)
    if "name" in update_data and update_data["name"] != db_appearance.name:
        existing_appearance = _get_appearance_by_name(db, name=update_data["name"])
        if existing_appearance:
            return OperationResult(status=OperationStatus.CONFLICT, data=existing_appearance)

    for key, value in update_data.items():
        setattr(db_appearance, key, value)
    db.add(db_appearance)
    db.commit()
    db.refresh(db_appearance)

    return OperationResult(status=OperationStatus.SUCCESS, data=db_appearance)


def delete_appearance(db: Session, appearance_id: int):
    db_appearance = db.query(models.Appearance).filter(models.Appearance.id == appearance_id).first()
    if db_appearance:
        db.delete(db_appearance)
        db.commit()
    return db_appearance
