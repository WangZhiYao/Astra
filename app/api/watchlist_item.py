import logging

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.core.exceptions import BusinessException
from app.core.operation_result import OperationStatus
from app.core.response import Response
from app.core.result_codes import ResultCode
from app.crud import crud_watchlist_item
from app.db.database import get_db
from app.models import User
from app.schemas import WatchlistItem, WatchlistItemCreate

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("", status_code=status.HTTP_201_CREATED, response_model=Response[WatchlistItem])
def create_watchlist_item(
        watchlist_id: int,
        item: WatchlistItemCreate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    logger.info(f"User {current_user.email} is adding item to watchlist {watchlist_id}.")
    operation_result = crud_watchlist_item.create_watchlist_item(
        db=db,
        user_id=current_user.id,
        watchlist_id=watchlist_id,
        item=item
    )

    if operation_result.status == OperationStatus.NOT_FOUND:
        logger.warning(f"Watchlist with ID {watchlist_id} not found for user {current_user.email}.")
        raise BusinessException(ResultCode.WATCHLIST_NOT_EXISTS)
    elif operation_result.status == OperationStatus.CONFLICT:
        logger.warning(f"Watchlist item already exists in watchlist {watchlist_id} for user {current_user.email}.")
        raise BusinessException(ResultCode.WATCHLIST_ITEM_ALREADY_EXISTS)

    logger.info(f"Watchlist item {operation_result.data.id} created successfully.")

    return Response(data=operation_result.data)


@router.delete("/{watchlist_item_id}", response_model=Response)
def delete_watchlist_item(
        watchlist_item_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    logger.info(f"User {current_user.email} is deleting watchlist item with ID: {watchlist_item_id}")
    operation_result = crud_watchlist_item.delete_watchlist_item(
        db=db,
        user_id=current_user.id,
        watchlist_item_id=watchlist_item_id
    )

    if operation_result.status == OperationStatus.NOT_FOUND:
        logger.warning(f"Watchlist item with ID {watchlist_item_id} not found for deletion by user {current_user.email}.")
        raise BusinessException(ResultCode.WATCHLIST_ITEM_NOT_EXISTS)

    logger.info(f"Watchlist item with ID {watchlist_item_id} deleted successfully.")

    return Response(message="Watchlist item deleted successfully")
