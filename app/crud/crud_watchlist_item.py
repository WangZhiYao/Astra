from typing import List

from sqlalchemy.orm import Session, joinedload, selectinload

import app.models as models
import app.schemas as schemas
from app.core.operation_result import OperationResult, OperationStatus
from app.core.paging import PagingData
from app.crud.crud_watchlist import get_watchlist_by_user


def _get_watchlist_item_by_watchlist_and_appearance(db: Session, watchlist_id: int, appearance_id: int):
    return db.query(models.WatchlistItem).filter(
        models.WatchlistItem.watchlist_id == watchlist_id,
        models.WatchlistItem.appearance_id == appearance_id
    ).first()


def get_watchlist_items_by_watchlist_id(
        db: Session,
        user_id: int,
        watchlist_id: int,
        page: int,
        page_size: int
) -> OperationResult[PagingData[schemas.WatchlistItem]]:
    # First, check if the watchlist exists and belongs to the user.
    watchlist = (
        db.query(models.Watchlist)
        .filter(
            models.Watchlist.user_id == user_id,
            models.Watchlist.id == watchlist_id
        )
        .first()
    )
    if not watchlist:
        return OperationResult(status=OperationStatus.NOT_FOUND)

    # Then, query the items with pagination and eager loading.
    query = (
        db.query(models.WatchlistItem)
        .options(
            selectinload(models.WatchlistItem.appearance).selectinload(models.Appearance.appearance_aliases),
            selectinload(models.WatchlistItem.appearance).selectinload(models.Appearance.appearance_types)
        )
        .filter(models.WatchlistItem.watchlist_id == watchlist_id)
    )

    total_count = query.count()

    offset = (page - 1) * page_size
    db_watchlist_items = (
        query.order_by(models.WatchlistItem.id)
        .offset(offset)
        .limit(page_size)
        .all()
    )

    items = [schemas.WatchlistItem.model_validate(item) for item in db_watchlist_items]

    return OperationResult(
        status=OperationStatus.SUCCESS,
        data=PagingData(items=items, total_count=total_count)
    )


def create_watchlist_item(
        db: Session,
        user_id: int,
        watchlist_id: int,
        item: schemas.WatchlistItemCreate
) -> OperationResult[schemas.WatchlistItem]:
    operation_result = get_watchlist_by_user(db=db, user_id=user_id, watchlist_id=watchlist_id)
    if operation_result.status == OperationStatus.NOT_FOUND:
        return OperationResult(status=OperationStatus.NOT_FOUND)

    existing_item = _get_watchlist_item_by_watchlist_and_appearance(
        db=db,
        watchlist_id=watchlist_id,
        appearance_id=item.appearance_id
    )

    if existing_item:
        return OperationResult(
            status=OperationStatus.CONFLICT,
            data=schemas.WatchlistItem.model_validate(existing_item)
        )

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


def delete_watchlist_item(db: Session, user_id: int, watchlist_item_id: int) -> OperationResult:
    db_watchlist_item = _get_watchlist_item_by_user(db=db, user_id=user_id, watchlist_item_id=watchlist_item_id)
    if not db_watchlist_item:
        return OperationResult(status=OperationStatus.NOT_FOUND)

    db.delete(db_watchlist_item)
    db.commit()

    return OperationResult(status=OperationStatus.SUCCESS)
