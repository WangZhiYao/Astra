from sqlalchemy.orm import Session

from app.models import WatchlistItem, Watchlist
from app.schemas import WatchlistItemCreate


def create_watchlist_item(db: Session, watchlist_id: int, item: WatchlistItemCreate):
    db_item = WatchlistItem(watchlist_id=watchlist_id, **item.model_dump())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


def get_watchlist_item_by_user(db: Session, user_id: int, watchlist_item_id: int):
    return db.query(WatchlistItem).join(Watchlist).filter(
        Watchlist.user_id == user_id,
        WatchlistItem.id == watchlist_item_id
    ).first()


def delete_watchlist_item(db: Session, watchlist_item_id: int):
    db_item = db.query(WatchlistItem).filter(WatchlistItem.id == watchlist_item_id).first()
    if db_item:
        db.delete(db_item)
        db.commit()
    return db_item
