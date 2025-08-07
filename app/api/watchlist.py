from typing import List
import logging

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.core.exceptions import BusinessException
from app.core.operation_result import OperationStatus
from app.core.response import Response
from app.core.result_codes import ResultCode
from app.crud import crud_watchlist
from app.db.database import get_db
from app.models import User
from app.schemas import Watchlist, WatchlistCreate, WatchlistUpdate

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("", status_code=status.HTTP_201_CREATED, response_model=Response[Watchlist])
def create_watchlist(
        watchlist: WatchlistCreate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    logger.info(f"User {current_user.email} is creating a new watchlist with name: {watchlist.name}")
    operation_result = crud_watchlist.create_watchlist(db=db, user_id=current_user.id, watchlist=watchlist)
    if operation_result.status == OperationStatus.CONFLICT:
        logger.warning(f"Watchlist with name {watchlist.name} already exists for user {current_user.email}.")
        raise BusinessException(ResultCode.WATCHLIST_ALREADY_EXISTS)

    logger.info(f"Watchlist {operation_result.data.name} created successfully with ID: {operation_result.data.id}")

    return Response(data=operation_result.data)


@router.get("", response_model=Response[List[Watchlist]])
def get_watchlists(
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    logger.info(f"User {current_user.email} is fetching their watchlists.")
    watchlists = crud_watchlist.get_watchlists_by_user(db=db, user_id=current_user.id)
    logger.info(f"Found {len(watchlists)} watchlists for user {current_user.email}.")
    return Response(data=watchlists)


@router.put("/{watchlist_id}", response_model=Response[Watchlist])
def update_watchlist(
        watchlist_id: int,
        watchlist: WatchlistUpdate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
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
        raise BusinessException(ResultCode.WATCHLIST_NOT_EXISTS)

    logger.info(f"Watchlist with ID {watchlist_id} updated successfully.")

    return Response(data=operation_result.data)


@router.delete("/{watchlist_id}", response_model=Response)
def delete_watchlist(
        watchlist_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    logger.info(f"User {current_user.email} is deleting watchlist with ID: {watchlist_id}")
    operation_result = crud_watchlist.delete_watchlist(db=db, user_id=current_user.id, watchlist_id=watchlist_id)

    if operation_result.status == OperationStatus.NOT_FOUND:
        logger.warning(f"Watchlist with ID {watchlist_id} not found for deletion by user {current_user.email}.")
        raise BusinessException(ResultCode.NOT_FOUND)

    logger.info(f"Watchlist with ID {watchlist_id} deleted successfully.")

    return Response(message="Watchlist deleted successfully")
