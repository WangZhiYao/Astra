from typing import List

from sqlalchemy.orm import Session

import app.models as models
import app.schemas as schemas
from app.core.operation_result import OperationResult, OperationStatus


def _get_appearance_type_by_name(db: Session, name: str):
    return db.query(models.AppearanceType).filter(models.AppearanceType.name == name).first()


def create_appearance_type(
        db: Session,
        appearance_type: schemas.AppearanceTypeCreate
) -> OperationResult[schemas.AppearanceType]:
    db_appearance_type = _get_appearance_type_by_name(db=db, name=appearance_type.name)
    if db_appearance_type:
        return OperationResult(
            status=OperationStatus.CONFLICT,
            data=schemas.AppearanceType.model_validate(db_appearance_type)
        )

    db_appearance_type = models.AppearanceType(name=appearance_type.name)
    db.add(db_appearance_type)
    db.commit()
    db.refresh(db_appearance_type)

    return OperationResult(
        status=OperationStatus.SUCCESS,
        data=schemas.AppearanceType.model_validate(db_appearance_type)
    )


def get_appearance_types(
        db: Session,
        page: int = 1,
        page_size: int = 100
) -> OperationResult[List[schemas.AppearanceType]]:
    offset = (page - 1) * page_size
    db_appearance_types = db.query(models.AppearanceType).offset(offset).limit(page_size).all()
    data = [schemas.AppearanceType.model_validate(db_appearance_type) for db_appearance_type in db_appearance_types]
    return OperationResult(status=OperationStatus.SUCCESS, data=data)


def update_appearance_type(
        db: Session,
        type_id: int,
        appearance_type: schemas.AppearanceTypeUpdate
) -> OperationResult[schemas.AppearanceType]:
    db_appearance_type = db.query(models.AppearanceType).filter(models.AppearanceType.id == type_id).first()
    if not db_appearance_type:
        return OperationResult(status=OperationStatus.NOT_FOUND)

    update_data = appearance_type.model_dump(exclude_unset=True)
    if "name" in update_data and update_data["name"] != db_appearance_type.name:
        existing_appearance_type = _get_appearance_type_by_name(db, name=update_data["name"])
        if existing_appearance_type:
            return OperationResult(
                status=OperationStatus.CONFLICT,
                data=schemas.AppearanceType.model_validate(existing_appearance_type)
            )

    for key, value in update_data.items():
        setattr(db_appearance_type, key, value)
    db.add(db_appearance_type)
    db.commit()
    db.refresh(db_appearance_type)

    return OperationResult(
        status=OperationStatus.SUCCESS,
        data=schemas.AppearanceType.model_validate(db_appearance_type)
    )


def delete_appearance_type(db: Session, type_id: int) -> OperationResult:
    db_appearance_type = db.query(models.AppearanceType).filter(models.AppearanceType.id == type_id).first()
    if not db_appearance_type:
        return OperationResult(status=OperationStatus.NOT_FOUND)
    db.delete(db_appearance_type)
    db.commit()
    return OperationResult(status=OperationStatus.SUCCESS)
