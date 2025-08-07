from sqlalchemy.orm import Session

import app.models as models
import app.schemas as schemas
from app.core.operation_result import OperationResult, OperationStatus


def get_watchlists_by_user(db: Session, user_id: int):
    return db.query(models.Watchlist).filter(models.Watchlist.user_id == user_id).all()


def _get_watchlist_by_user_and_name(db: Session, user_id: int, name: str):
    return db.query(models.Watchlist).filter(models.Watchlist.user_id == user_id, models.Watchlist.name == name).first()


def create_watchlist(db: Session, user_id: int, watchlist: schemas.WatchlistCreate):
    existing_watchlist = _get_watchlist_by_user_and_name(db=db, user_id=user_id, name=watchlist.name)
    if existing_watchlist:
        return OperationResult(status=OperationStatus.CONFLICT,
                               data=schemas.Watchlist.model_validate(existing_watchlist))

    db_watchlist = models.Watchlist(user_id=user_id, **watchlist.model_dump())
    db.add(db_watchlist)
    db.commit()
    db.refresh(db_watchlist)

    return OperationResult(status=OperationStatus.SUCCESS, data=db_watchlist)


def get_watchlist_by_user(db: Session, user_id: int, watchlist_id: int):
    return db.query(models.Watchlist).filter(models.Watchlist.user_id == user_id,
                                             models.Watchlist.id == watchlist_id).first()


def update_watchlist(
        db: Session,
        user_id: int,
        watchlist_id: int,
        watchlist: schemas.WatchlistUpdate
) -> OperationResult[schemas.Watchlist]:
    db_watchlist = get_watchlist_by_user(db=db, user_id=user_id, watchlist_id=watchlist_id)
    if not db_watchlist:
        return OperationResult(status=OperationStatus.NOT_FOUND)

    update_data = watchlist.model_dump(exclude_unset=True)
    if "name" in update_data and update_data["name"] != db_watchlist.name:
        existing_watchlist = _get_watchlist_by_user_and_name(db=db, user_id=user_id, name=update_data["name"])
        if existing_watchlist:
            return OperationResult(status=OperationStatus.CONFLICT,
                                   data=schemas.Watchlist.model_validate(existing_watchlist))

    for key, value in update_data.items():
        setattr(db_watchlist, key, value)
    db.add(db_watchlist)
    db.commit()
    db.refresh(db_watchlist)

    return OperationResult(status=OperationStatus.SUCCESS, data=schemas.Watchlist.model_validate(db_watchlist))


def delete_watchlist(db: Session, user_id: int, watchlist_id: int):
    db_watchlist = get_watchlist_by_user(db, user_id, watchlist_id)
    if not db_watchlist:
        return OperationResult(status=OperationStatus.NOT_FOUND)

    db.delete(db_watchlist)
    db.commit()

    return OperationResult(status=OperationStatus.SUCCESS, data=schemas.Watchlist.model_validate(db_watchlist))
