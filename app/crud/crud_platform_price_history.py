from typing import List, Optional

from sqlalchemy.orm import Session

from app.models import PlatformPriceHistory
from app.schemas import PlatformPriceHistoryCreate


def create_platform_price_histories(db: Session, histories: List[PlatformPriceHistoryCreate]):
    history_dicts = [history.model_dump() for history in histories]
    db.bulk_insert_mappings(PlatformPriceHistory, history_dicts)
    db.commit()
    return len(history_dicts)


def get_platform_price_histories(
        db: Session,
        page: int = 1,
        page_size: int = 100,
        platform_id: Optional[int] = None,
        appearance_id: Optional[int] = None
) -> List[PlatformPriceHistory]:
    query = db.query(PlatformPriceHistory)

    if platform_id:
        query = query.filter(PlatformPriceHistory.platform_id == platform_id)
    if appearance_id:
        query = query.filter(PlatformPriceHistory.appearance_id == appearance_id)

    offset = (page - 1) * page_size
    return query.offset(offset).limit(page_size).all()


def delete_platform_price_history(db: Session, history_id: int):
    db_history = db.query(PlatformPriceHistory).filter(PlatformPriceHistory.id == history_id).first()
    if db_history:
        db.delete(db_history)
        db.commit()
    return db_history
