from sqlalchemy.orm import Session

from app.models import Watchlist
from app.schemas import WatchlistCreate


def get_watchlist_by_user(db: Session, user_id: int, watchlist_id: int):
    return db.query(Watchlist).filter(Watchlist.user_id == user_id, Watchlist.id == watchlist_id).first()


def get_watchlists_by_user(db: Session, user_id: int):
    return db.query(Watchlist).filter(Watchlist.user_id == user_id).all()


def create_watchlist(db: Session, user_id: int, watchlist: WatchlistCreate):
    db_watchlist = Watchlist(user_id=user_id, **watchlist.model_dump())
    db.add(db_watchlist)
    db.commit()
    db.refresh(db_watchlist)
    return db_watchlist


def delete_watchlist(db: Session, user_id: int, watchlist_id: int):
    db_watchlist = get_watchlist_by_user(db, user_id, watchlist_id)
    if db_watchlist:
        db.delete(db_watchlist)
        db.commit()
    return db_watchlist
