from typing import List

from sqlalchemy.orm import Session

from app.models import PlatformPriceHistory
from app.schemas import PlatformPriceHistoryCreate


def create_platform_price_histories(db: Session, histories: List[PlatformPriceHistoryCreate]):
    history_dicts = [history.model_dump() for history in histories]
    db.bulk_insert_mappings(PlatformPriceHistory, history_dicts)
    db.commit()
    return len(history_dicts)
