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


@router.post("", status_code=status.HTTP_201_CREATED, response_model=Response[WatchlistItem])
def create_watchlist_item(
        watchlist_id: int,
        item: WatchlistItemCreate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    operation_result = crud_watchlist_item.create_watchlist_item(
        db=db,
        user_id=current_user.id,
        watchlist_id=watchlist_id,
        item=item
    )

    if operation_result.status == OperationStatus.NOT_FOUND:
        return BusinessException(ResultCode.WATCHLIST_NOT_EXISTS)
    elif operation_result.status == OperationStatus.CONFLICT:
        raise BusinessException(ResultCode.WATCHLIST_ITEM_ALREADY_EXISTS)

    return Response(data=operation_result.data)


@router.delete("/{watchlist_item_id}")
def delete_watchlist_item(
        watchlist_item_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    operation_result = crud_watchlist_item.delete_watchlist_item(
        db=db,
        user_id=current_user.id,
        watchlist_item_id=watchlist_item_id
    )

    if operation_result.status == OperationStatus.NOT_FOUND:
        return BusinessException(ResultCode.WATCHLIST_ITEM_NOT_EXISTS)

    return Response(code=204, message="Watchlist item deleted successfully")
