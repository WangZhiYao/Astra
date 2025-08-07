import logging
from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

import app.models as models
import app.schemas as schemas
from app.core.dependencies import get_current_user
from app.core.exceptions import BusinessException
from app.core.operation_result import OperationStatus
from app.core.response import Response
from app.core.result_codes import ResultCode
from app.crud import crud_watchlist
from app.db.database import get_db

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("", status_code=status.HTTP_201_CREATED, response_model=Response[schemas.Watchlist])
def create_watchlist(
        watchlist: schemas.WatchlistCreate,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(get_current_user)
):
    logger.info(f"User {current_user.email} is creating a new watchlist with name: {watchlist.name}")
    operation_result = crud_watchlist.create_watchlist(db=db, user_id=current_user.id, watchlist=watchlist)
    if operation_result.status == OperationStatus.CONFLICT:
        logger.warning(f"Watchlist with name {watchlist.name} already exists for user {current_user.email}.")
        raise BusinessException(ResultCode.WATCHLIST_ALREADY_EXISTS)

    logger.info(f"Watchlist {operation_result.data.name} created successfully with ID: {operation_result.data.id}")

    return Response(data=operation_result.data)


@router.get("", response_model=Response[List[schemas.Watchlist]])
def get_watchlists(
        db: Session = Depends(get_db),
        current_user: models.User = Depends(get_current_user)
):
    logger.info(f"User {current_user.email} is fetching their watchlists.")
    operation_result = crud_watchlist.get_watchlists_by_user(db=db, user_id=current_user.id)
    logger.info(f"Found {len(operation_result.data)} watchlists for user {current_user.email}.")
    return Response(data=operation_result.data)


@router.put("/{watchlist_id}", response_model=Response[schemas.Watchlist])
def update_watchlist(
        watchlist_id: int,
        watchlist: schemas.WatchlistUpdate,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(get_current_user)
):
    logger.info(f"User {current_user.email} is updating watchlist with ID: {watchlist_id}")
    operation_result = crud_watchlist.update_watchlist(
        db=db,
        user_id=current_user.id,
        watchlist_id=watchlist_id,
        watchlist=watchlist
    )

    if operation_result.status == OperationStatus.NOT_FOUND:
        logger.warning(f"Watchlist with ID {watchlist_id} not found for update by user {current_user.email}.")
        raise BusinessException(ResultCode.NOT_FOUND)
    elif operation_result.status == OperationStatus.CONFLICT:
        logger.warning(f"Watchlist update failed due to conflict for watchlist ID: {watchlist_id}")
        raise BusinessException(ResultCode.WATCHLIST_ALREADY_EXISTS)

    logger.info(f"Watchlist with ID {watchlist_id} updated successfully.")

    return Response(data=operation_result.data)


@router.delete("/{watchlist_id}", response_model=Response)
def delete_watchlist(
        watchlist_id: int,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(get_current_user)
):
    logger.info(f"User {current_user.email} is deleting watchlist with ID: {watchlist_id}")
    operation_result = crud_watchlist.delete_watchlist(db=db, user_id=current_user.id, watchlist_id=watchlist_id)

    if operation_result.status == OperationStatus.NOT_FOUND:
        logger.warning(f"Watchlist with ID {watchlist_id} not found for deletion by user {current_user.email}.")
        raise BusinessException(ResultCode.NOT_FOUND)

    logger.info(f"Watchlist with ID {watchlist_id} deleted successfully.")

    return Response(message="Watchlist deleted successfully")