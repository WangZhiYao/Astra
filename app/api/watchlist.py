from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.core.response import Response
from app.crud import crud_watchlist
from app.db.database import get_db
from app.models import User
from app.schemas import watchlist as watchlist_schema

router = APIRouter()


@router.post("", status_code=status.HTTP_201_CREATED, response_model=Response[watchlist_schema.Watchlist])
def create_watchlist(
        watchlist: watchlist_schema.WatchlistCreate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    new_watchlist = crud_watchlist.create_watchlist(db=db, user_id=current_user.id, watchlist=watchlist)
    return Response(data=new_watchlist)


@router.get("", response_model=Response[List[watchlist_schema.Watchlist]])
def get_watchlists(
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    watchlists = crud_watchlist.get_watchlists_by_user(db=db, user_id=current_user.id)
    return Response(data=watchlists)


@router.delete("/{watchlist_id}", response_model=Response)
def delete_watchlist(
        watchlist_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    crud_watchlist.delete_watchlist(db=db, user_id=current_user.id, watchlist_id=watchlist_id)
    return Response(code=204, message="Watchlist deleted successfully")
