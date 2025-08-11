from sqlalchemy.orm import Session

import app.models as models
import app.schemas as schemas
from app.core.operation_result import OperationResult, OperationStatus
from app.core.paging import PagingData


def _get_platform_by_name(db: Session, name: str):
    return db.query(models.Platform).filter(models.Platform.name == name).first()


def create_platform(db: Session, platform: schemas.PlatformCreate) -> OperationResult[schemas.Platform]:
    db_platform = _get_platform_by_name(db=db, name=platform.name)
    if db_platform:
        return OperationResult(status=OperationStatus.CONFLICT, data=schemas.Platform.model_validate(db_platform))

    db_platform = models.Platform(name=platform.name)
    db.add(db_platform)
    db.commit()
    db.refresh(db_platform)

    return OperationResult(status=OperationStatus.SUCCESS, data=schemas.Platform.model_validate(db_platform))


def get_platform_by_id(db: Session, platform_id: int) -> OperationResult[schemas.Platform]:
    db_platform = db.query(models.Platform).filter(models.Platform.id == platform_id).first()
    if not db_platform:
        return OperationResult(status=OperationStatus.NOT_FOUND)

    return OperationResult(status=OperationStatus.SUCCESS, data=schemas.Platform.model_validate(db_platform))


def get_platforms(db: Session, page: int = 1, page_size: int = 100) -> OperationResult[PagingData[schemas.Platform]]:
    total_count = db.query(models.Platform).count()
    if total_count == 0:
        return OperationResult(
            status=OperationStatus.SUCCESS,
            data=PagingData(items=[], total_count=0)
        )

    offset = (page - 1) * page_size
    db_platforms = (
        db.query(models.Platform)
        .order_by(models.Platform.id)
        .offset(offset)
        .limit(page_size)
        .all()
    )

    items = [schemas.Platform.model_validate(db_platform) for db_platform in db_platforms]

    return OperationResult(
        status=OperationStatus.SUCCESS,
        data=PagingData(items=items, total_count=total_count)
    )


def update_platform(
        db: Session,
        platform_id: int,
        platform: schemas.PlatformUpdate
) -> OperationResult[schemas.Platform]:
    operation_result = get_platform_by_id(db, platform_id=platform_id)
    if operation_result.status == OperationStatus.NOT_FOUND:
        return OperationResult(status=OperationStatus.NOT_FOUND)

    db_platform = operation_result.data

    update_data = platform.model_dump(exclude_unset=True)
    if "name" in update_data and update_data["name"] != db_platform.name:
        existing_platform = _get_platform_by_name(db, name=update_data["name"])
        if existing_platform:
            return OperationResult(
                status=OperationStatus.CONFLICT,
                data=schemas.Platform.model_validate(existing_platform)
            )

    for key, value in update_data.items():
        setattr(db_platform, key, value)
    db.add(db_platform)
    db.commit()
    db.refresh(db_platform)

    return OperationResult(status=OperationStatus.SUCCESS, data=schemas.Platform.model_validate(db_platform))


def delete_platform(db: Session, platform_id: int) -> OperationResult:
    operation_result = get_platform_by_id(db, platform_id=platform_id)
    if operation_result.status == OperationStatus.NOT_FOUND:
        return OperationResult(status=OperationStatus.NOT_FOUND)

    db_platform = operation_result.data

    db.delete(db_platform)
    db.commit()

    return OperationResult(status=OperationStatus.SUCCESS)
