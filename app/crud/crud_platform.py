from typing import List

from sqlalchemy.orm import Session

from app.core.operation_result import OperationResult, OperationStatus
from app.models import Platform
from app.schemas import PlatformCreate, PlatformUpdate


def get_platform_by_id(db: Session, platform_id: int):
    return db.query(Platform).filter(Platform.id == platform_id).first()


def _get_platform_by_name(db: Session, name: str):
    return db.query(Platform).filter(Platform.name == name).first()


def create_platform(db: Session, platform: PlatformCreate):
    db_platform = _get_platform_by_name(db, name=platform.name)
    if db_platform:
        return OperationResult(status=OperationStatus.CONFLICT, data=db_platform)

    db_platform = Platform(name=platform.name)
    db.add(db_platform)
    db.commit()
    db.refresh(db_platform)

    return OperationResult(status=OperationStatus.SUCCESS, data=db_platform)


def get_platforms(db: Session, page: int = 1, page_size: int = 100) -> List[Platform]:
    offset = (page - 1) * page_size
    return db.query(Platform).offset(offset).limit(page_size).all()


def update_platform(db: Session, platform_id: int, platform: PlatformUpdate) -> OperationResult[Platform]:
    db_platform = db.query(Platform).filter(Platform.id == platform_id).first()
    if not db_platform:
        return OperationResult(status=OperationStatus.NOT_FOUND)

    update_data = platform.model_dump(exclude_unset=True)
    if "name" in update_data and update_data["name"] != db_platform.name:
        existing_platform = _get_platform_by_name(db, name=update_data["name"])
        if existing_platform:
            return OperationResult(status=OperationStatus.CONFLICT, data=existing_platform)

    for key, value in update_data.items():
        setattr(db_platform, key, value)
    db.add(db_platform)
    db.commit()
    db.refresh(db_platform)

    return OperationResult(status=OperationStatus.SUCCESS, data=db_platform)


def delete_platform(db: Session, platform_id: int):
    db_platform = db.query(Platform).filter(Platform.id == platform_id).first()
    if db_platform:
        db.delete(db_platform)
        db.commit()
    return db_platform
