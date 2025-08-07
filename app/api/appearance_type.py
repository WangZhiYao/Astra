import logging
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
from app.crud import crud_appearance_type
from app.db.database import get_db

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("", status_code=status.HTTP_201_CREATED, response_model=Response[schemas.AppearanceType])
def create_appearance_type(
        appearance_type: schemas.AppearanceTypeCreate,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(require_admin)
):
    logger.info(f"User {current_user.email} is creating a new appearance type with name: {appearance_type.name}")
    operation_result = crud_appearance_type.create_appearance_type(db, appearance_type=appearance_type)
    if operation_result.status == OperationStatus.CONFLICT:
        logger.warning(f"Appearance type with name {appearance_type.name} already exists.")
        raise BusinessException(ResultCode.APPEARANCE_TYPE_ALREADY_EXISTS)

    logger.info(f"Appearance type {operation_result.data.name} created successfully with ID: {operation_result.data.id}")

    return Response(data=operation_result.data)


@router.get("", response_model=Response[List[schemas.AppearanceType]])
def get_appearance_types(
        page: int = 1,
        page_size: int = 100,
        db: Session = Depends(get_db)
):
    logger.info(f"Fetching appearance types with page: {page}, page_size: {page_size}")
    operation_result = crud_appearance_type.get_appearance_types(db, page=page, page_size=page_size)
    logger.info(f"Found {len(operation_result.data)} appearance types.")
    return Response(data=operation_result.data)


@router.put("/{type_id}", response_model=Response[schemas.AppearanceType])
def update_appearance_type(
        type_id: int,
        appearance_type: schemas.AppearanceTypeUpdate,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(require_admin)
):
    logger.info(f"User {current_user.email} is updating appearance type with ID: {type_id}")
    operation_result = crud_appearance_type.update_appearance_type(
        db,
        type_id=type_id,
        appearance_type=appearance_type
    )
    if operation_result.status == OperationStatus.NOT_FOUND:
        logger.warning(f"Appearance type with ID {type_id} not found for update.")
        raise BusinessException(ResultCode.NOT_FOUND)
    elif operation_result.status == OperationStatus.CONFLICT:
        logger.warning(f"Appearance type with name {appearance_type.name} already exists.")
        raise BusinessException(ResultCode.APPEARANCE_TYPE_ALREADY_EXISTS)

    logger.info(f"Appearance type with ID {type_id} updated successfully.")
    return Response(data=operation_result.data)


@router.delete("/{type_id}", response_model=Response)
def delete_appearance_type(
        type_id: int,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(require_admin)
):
    logger.info(f"User {current_user.email} is deleting appearance type with ID: {type_id}")
    operation_result = crud_appearance_type.delete_appearance_type(db, type_id=type_id)
    if operation_result.status == OperationStatus.NOT_FOUND:
        logger.warning(f"Appearance type with ID {type_id} not found for deletion.")
        raise BusinessException(ResultCode.NOT_FOUND)
    logger.info(f"Appearance type with ID {type_id} deleted successfully.")
    return Response(message="Appearance type deleted successfully")
