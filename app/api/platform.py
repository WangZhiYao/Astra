from typing import List
import logging

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
logger = logging.getLogger(__name__)


@router.post("", status_code=status.HTTP_201_CREATED, response_model=Response[schemas.Platform])
def create_platform(
        platform: schemas.PlatformCreate,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(require_admin)
):
    logger.info(f"User {current_user.email} is creating a new platform with name: {platform.name}")
    operation_result = crud_platform.create_platform(db=db, platform=platform)
    if operation_result.status == OperationStatus.CONFLICT:
        logger.warning(f"Platform with name {platform.name} already exists.")
        raise BusinessException(ResultCode.PLATFORM_ALREADY_EXISTS)

    logger.info(f"Platform {operation_result.data.name} created successfully with ID: {operation_result.data.id}")

    return Response(data=operation_result.data)


@router.get("/{platform_id}", response_model=Response[schemas.Platform])
def get_platform(
        platform_id: int,
        db: Session = Depends(get_db)
):
    logger.info(f"Fetching platform with ID: {platform_id}")
    db_platform = crud_platform.get_platform_by_id(db, platform_id=platform_id)
    if db_platform is None:
        logger.warning(f"Platform with ID {platform_id} not found.")
        raise BusinessException(ResultCode.NOT_FOUND)
    logger.info(f"Platform with ID {platform_id} fetched successfully.")
    return Response(data=db_platform)


@router.get("", response_model=Response[List[schemas.Platform]])
def get_platforms(
        page: int = 1,
        page_size: int = 100,
        db: Session = Depends(get_db)
):
    logger.info(f"Fetching platforms with page: {page}, page_size: {page_size}")
    platforms = crud_platform.get_platforms(db, page=page, page_size=page_size)
    logger.info(f"Found {len(platforms)} platforms.")
    return Response(data=platforms)


@router.put("/{platform_id}", response_model=Response[schemas.Platform])
def update_platform(
        platform_id: int,
        platform: schemas.PlatformUpdate,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(require_admin)
):
    logger.info(f"User {current_user.email} is updating platform with ID: {platform_id}")
    operation_result = crud_platform.update_platform(db, platform_id=platform_id, platform=platform)
    if operation_result.status == OperationStatus.CONFLICT:
        logger.warning(f"Platform update failed due to conflict for platform ID: {platform_id}")
        raise BusinessException(ResultCode.PLATFORM_ALREADY_EXISTS)
    elif operation_result.status == OperationStatus.NOT_FOUND:
        logger.warning(f"Platform with ID {platform_id} not found for update.")
        raise BusinessException(ResultCode.NOT_FOUND)

    logger.info(f"Platform with ID {platform_id} updated successfully.")

    return Response(data=operation_result.data)


@router.delete("/{platform_id}", response_model=Response)
def delete_platform(
        platform_id: int,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(require_admin)
):
    logger.info(f"User {current_user.email} is deleting platform with ID: {platform_id}")
    db_platform = crud_platform.delete_platform(db, platform_id=platform_id)
    if db_platform is None:
        logger.warning(f"Platform with ID {platform_id} not found for deletion.")
        raise BusinessException(ResultCode.NOT_FOUND)
    logger.info(f"Platform with ID {platform_id} deleted successfully.")
    return Response(message="Platform deleted successfully")
