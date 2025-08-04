from typing import List

from sqlalchemy.orm import Session

from app.core.operation_result import OperationResult, OperationStatus
from app.models import AppearanceType
from app.schemas import AppearanceTypeCreate, AppearanceTypeUpdate


def _get_appearance_type_by_name(db: Session, name: str):
    return db.query(AppearanceType).filter(AppearanceType.name == name).first()


def create_appearance_type(db: Session, appearance_type: AppearanceTypeCreate):
    db_appearance_type = _get_appearance_type_by_name(db=db, name=appearance_type.name)
    if db_appearance_type:
        return OperationResult(status=OperationStatus.CONFLICT, data=db_appearance_type)

    db_appearance_type = AppearanceType(name=appearance_type.name)
    db.add(db_appearance_type)
    db.commit()
    db.refresh(db_appearance_type)

    return OperationResult(status=OperationStatus.SUCCESS, data=db_appearance_type)


def get_appearance_types(db: Session, page: int = 1, page_size: int = 100) -> List[AppearanceType]:
    offset = (page - 1) * page_size
    return db.query(AppearanceType).offset(offset).limit(page_size).all()


def update_appearance_type(
        db: Session,
        type_id: int,
        appearance_type: AppearanceTypeUpdate
) -> OperationResult[AppearanceType]:
    db_appearance_type = db.query(AppearanceType).filter(AppearanceType.id == type_id).first()
    if not db_appearance_type:
        return OperationResult(status=OperationStatus.NOT_FOUND)

    update_data = appearance_type.model_dump(exclude_unset=True)
    if "name" in update_data and update_data["name"] != db_appearance_type.name:
        existing_appearance_type = _get_appearance_type_by_name(db, name=update_data["name"])
        if existing_appearance_type:
            return OperationResult(status=OperationStatus.CONFLICT, data=existing_appearance_type)

    for key, value in update_data.items():
        setattr(db_appearance_type, key, value)
    db.add(db_appearance_type)
    db.commit()
    db.refresh(db_appearance_type)

    return OperationResult(status=OperationStatus.SUCCESS, data=db_appearance_type)


def delete_appearance_type(db: Session, type_id: int):
    db_appearance_type = db.query(AppearanceType).filter(AppearanceType.id == type_id).first()
    if db_appearance_type:
        db.delete(db_appearance_type)
        db.commit()
    return db_appearance_type
