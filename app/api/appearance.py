import logging
from typing import Optional

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

import app.models as models
import app.schemas as schemas
from app.core.dependencies import require_admin
from app.core.exceptions import BusinessException
from app.core.operation_result import OperationStatus
from app.core.paging import PagingData
from app.core.response import Response
from app.core.result_codes import ResultCode
from app.crud import crud_appearance
from app.db.database import get_db

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("", status_code=status.HTTP_201_CREATED, response_model=Response[schemas.Appearance])
def create_appearance(
        appearance: schemas.AppearanceCreate,
        db: Session = Depends(get_db),
        _: models.User = Depends(require_admin)
):
    logger.info(f"User {_.email} is creating a new appearance with name: {appearance.name}")
    operation_result = crud_appearance.create_appearance(db=db, appearance=appearance)
    if operation_result.status == OperationStatus.CONFLICT:
        logger.warning(f"Appearance with name {appearance.name} already exists.")
        raise BusinessException(ResultCode.APPEARANCE_ALREADY_EXISTS)

    new_appearance = operation_result.data
    logger.info(f"Appearance {new_appearance.name} created successfully with ID: {new_appearance.id}")
    return Response(data=new_appearance)


@router.get("/{appearance_id}", response_model=Response[schemas.Appearance])
def get_appearance(
        appearance_id: int,
        db: Session = Depends(get_db)
):
    logger.info(f"Fetching appearance with ID: {appearance_id}")
    operation_result = crud_appearance.get_appearance_by_id(db, appearance_id=appearance_id)
    if operation_result.status == OperationStatus.NOT_FOUND:
        logger.warning(f"Appearance with ID {appearance_id} not found.")
        raise BusinessException(ResultCode.NOT_FOUND)

    logger.info(f"Appearance with ID {appearance_id} fetched successfully.")

    return Response(data=operation_result.data)


@router.get("", response_model=Response[PagingData[schemas.Appearance]])
def get_appearances(
        page: int = 1,
        page_size: int = 100,
        search_query: Optional[str] = None,
        db: Session = Depends(get_db)
):
    logger.info(f"Fetching appearances with page: {page}, page_size: {page_size}, search_query: {search_query}")
    operation_result = crud_appearance.get_appearances(db, page=page, page_size=page_size, search_query=search_query)
    logger.info(f"Found {len(operation_result.data.items)} appearances, total: {operation_result.data.total_count}")
    return Response(data=operation_result.data)


@router.put("/{appearance_id}", response_model=Response[schemas.Appearance])
def update_appearance(
        appearance_id: int,
        appearance: schemas.AppearanceUpdate,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(require_admin)
):
    logger.info(f"User {current_user.email} is updating appearance with ID: {appearance_id}")
    operation_result = crud_appearance.update_appearance(db, appearance_id=appearance_id, appearance=appearance)
    if operation_result.status == OperationStatus.CONFLICT:
        logger.warning(f"Appearance with name {appearance.name} already exists.")
        raise BusinessException(ResultCode.APPEARANCE_ALREADY_EXISTS)
    elif operation_result.status == OperationStatus.NOT_FOUND:
        logger.warning(f"Appearance with ID {appearance_id} not found.")
        raise BusinessException(ResultCode.NOT_FOUND)

    logger.info(f"Appearance with ID {appearance_id} updated successfully.")

    return Response(data=operation_result.data)


@router.delete("/{appearance_id}", response_model=Response)
def delete_appearance(
        appearance_id: int,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(require_admin)
):
    logger.info(f"User {current_user.email} is deleting appearance with ID: {appearance_id}")
    operation_result = crud_appearance.delete_appearance(db, appearance_id=appearance_id)
    if operation_result.status == OperationStatus.NOT_FOUND:
        logger.warning(f"Appearance with ID {appearance_id} not found for deletion.")
        raise BusinessException(ResultCode.NOT_FOUND)
    logger.info(f"Appearance with ID {appearance_id} deleted successfully.")
    return Response(message="Appearance deleted successfully")
