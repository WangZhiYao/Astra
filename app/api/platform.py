from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

import app.models as models
import app.schemas as schemas
from app.core.dependencies import require_admin
from app.core.exceptions import BusinessException
from app.core.operation_result import OperationStatus
from app.core.response import Response
from app.core.result_codes import ResultCode
from app.crud import crud_platform
from app.db.database import get_db

router = APIRouter()


@router.post("", status_code=status.HTTP_201_CREATED, response_model=Response[schemas.Platform])
def create_platform(
        platform: schemas.PlatformCreate,
        db: Session = Depends(get_db),
        _: models.User = Depends(require_admin)
):
    operation_result = crud_platform.create_platform(db=db, platform=platform)
    if operation_result.status == OperationStatus.CONFLICT:
        raise BusinessException(ResultCode.PLATFORM_ALREADY_EXISTS)

    return Response(data=operation_result.data)


@router.get("/{platform_id}", response_model=Response[schemas.Platform])
def get_platform(
        platform_id: int,
        db: Session = Depends(get_db)
):
    db_platform = crud_platform.get_platform_by_id(db, platform_id=platform_id)
    if db_platform is None:
        raise BusinessException(ResultCode.NOT_FOUND)
    return Response(data=db_platform)


@router.get("", response_model=Response[List[schemas.Platform]])
def get_platforms(
        page: int = 1,
        page_size: int = 100,
        db: Session = Depends(get_db)
):
    platforms = crud_platform.get_platforms(db, page=page, page_size=page_size)
    return Response(data=platforms)


@router.put("/{platform_id}", response_model=Response[schemas.Platform])
def update_platform(
        platform_id: int,
        platform: schemas.PlatformUpdate,
        db: Session = Depends(get_db),
        _: models.User = Depends(require_admin)
):
    operation_result = crud_platform.update_platform(db, platform_id=platform_id, platform=platform)
    if operation_result.status == OperationStatus.CONFLICT:
        raise BusinessException(ResultCode.PLATFORM_ALREADY_EXISTS)
    elif operation_result.status == OperationStatus.NOT_FOUND:
        raise BusinessException(ResultCode.NOT_FOUND)

    return Response(data=operation_result.data)


@router.delete("/{platform_id}", response_model=Response)
def delete_platform(
        platform_id: int,
        db: Session = Depends(get_db),
        _: models.User = Depends(require_admin)
):
    db_platform = crud_platform.delete_platform(db, platform_id=platform_id)
    if db_platform is None:
        raise BusinessException(ResultCode.NOT_FOUND)
    return Response(message="Platform deleted successfully")
