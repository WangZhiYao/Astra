from typing import List

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


@router.post("", status_code=status.HTTP_201_CREATED, response_model=Response[Watchlist])
def create_watchlist(
        watchlist: WatchlistCreate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    operation_result = crud_watchlist.create_watchlist(db=db, user_id=current_user.id, watchlist=watchlist)
    if operation_result.status == OperationStatus.CONFLICT:
        raise BusinessException(ResultCode.WATCHLIST_ALREADY_EXISTS)

    return Response(data=operation_result.data)


@router.get("", response_model=Response[List[Watchlist]])
def get_watchlists(
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    watchlists = crud_watchlist.get_watchlists_by_user(db=db, user_id=current_user.id)
    return Response(data=watchlists)


@router.put("/{watchlist_id}", response_model=Response[Watchlist])
def update_watchlist(
        watchlist_id: int,
        watchlist: WatchlistUpdate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    operation_result = crud_watchlist.update_watchlist(
        db=db,
        user_id=current_user.id,
        watchlist_id=watchlist_id,
        watchlist=watchlist
    )

    if operation_result.status == OperationStatus.NOT_FOUND:
        raise BusinessException(ResultCode.NOT_FOUND)
    elif operation_result.status == OperationStatus.CONFLICT:
        raise BusinessException(ResultCode.WATCHLIST_NOT_EXISTS)

    return Response(data=operation_result.data)


@router.delete("/{watchlist_id}", response_model=Response)
def delete_watchlist(
        watchlist_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    operation_result = crud_watchlist.delete_watchlist(db=db, user_id=current_user.id, watchlist_id=watchlist_id)

    if operation_result.status == OperationStatus.NOT_FOUND:
        raise BusinessException(ResultCode.NOT_FOUND)

    return Response(message="Watchlist deleted successfully")
