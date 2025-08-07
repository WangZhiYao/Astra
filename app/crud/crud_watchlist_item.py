from sqlalchemy.orm import Session

import app.models as models
import app.schemas as schemas
from app.core.operation_result import OperationResult, OperationStatus
from app.crud.crud_watchlist import get_watchlist_by_user


def _get_watchlist_item_by_watchlist_and_appearance(db: Session, watchlist_id: int, appearance_id: int):
    return db.query(models.WatchlistItem).filter(
        models.WatchlistItem.watchlist_id == watchlist_id,
        models.WatchlistItem.appearance_id == appearance_id
    ).first()


def create_watchlist_item(db: Session, user_id: int, watchlist_id: int, item: schemas.WatchlistItemCreate):
    watchlist = get_watchlist_by_user(db=db, user_id=user_id, watchlist_id=watchlist_id)
    if not watchlist:
        return OperationResult(status=OperationStatus.NOT_FOUND)

    existing_item = _get_watchlist_item_by_watchlist_and_appearance(
        db=db,
        watchlist_id=watchlist_id,
        appearance_id=item.appearance_id
    )

    if existing_item:
        return OperationResult(status=OperationStatus.CONFLICT, data=existing_item)

    db_item = models.WatchlistItem(watchlist_id=watchlist_id, **item.model_dump())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)

    return OperationResult(status=OperationStatus.SUCCESS, data=schemas.WatchlistItem.model_validate(db_item))


def _get_watchlist_item_by_user(db: Session, user_id: int, watchlist_item_id: int):
    return db.query(models.WatchlistItem).join(models.Watchlist).filter(
        models.Watchlist.user_id == user_id,
        models.WatchlistItem.id == watchlist_item_id
    ).first()


def delete_watchlist_item(db: Session, user_id: int, watchlist_item_id: int):
    db_item = _get_watchlist_item_by_user(db=db, user_id=user_id, watchlist_item_id=watchlist_item_id)
    if not db_item:
        return OperationResult(status=OperationStatus.NOT_FOUND)

    db.delete(db_item)
    db.commit()
    return OperationResult(status=OperationStatus.SUCCESS, data=schemas.WatchlistItem.model_validate(db_item))
