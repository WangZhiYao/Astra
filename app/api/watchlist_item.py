from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.core.exceptions import BusinessException
from app.core.response import Response
from app.core.result_codes import ResultCode
from app.crud import crud_watchlist, crud_watchlist_item
from app.db.database import get_db
from app.models import User
from app.schemas import watchlist_item as watchlist_item_schema

router = APIRouter()


@router.post("", status_code=status.HTTP_201_CREATED, response_model=Response[watchlist_item_schema.WatchlistItem])
def create_watchlist_item(
        watchlist_id: int,
        item: watchlist_item_schema.WatchlistItemCreate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)  # Ensure user is authenticated
):
    watchlist = crud_watchlist.get_watchlist_by_user(db, user_id=current_user.id, watchlist_id=watchlist_id).first()
    if not watchlist:
        return BusinessException(ResultCode.WATCHLIST_NOT_EXISTS)

    new_item = crud_watchlist_item.create_watchlist_item(db=db, watchlist_id=watchlist_id, item=item)
    return Response(data=new_item)


@router.delete("/{watchlist_item_id}")
def delete_watchlist_item(
        watchlist_item_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)  # Ensure user is authenticated
):
    watchlist_item = crud_watchlist_item.get_watchlist_item_by_user(db=db, user_id=current_user.id,
                                                                    watchlist_item_id=watchlist_item_id)
    if not watchlist_item:
        return BusinessException(ResultCode.WATCHLIST_ITEM_NOT_EXISTS)

    crud_watchlist_item.delete_watchlist_item(db=db, watchlist_item_id=watchlist_item_id)
    return Response(code=204, message="Watchlist item deleted successfully")
