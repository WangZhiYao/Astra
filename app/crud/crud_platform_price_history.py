from typing import List, Optional

from sqlalchemy.orm import Session

import app.models as models
import app.schemas as schemas
from app.core.operation_result import OperationResult, OperationStatus


def create_platform_price_histories(
        db: Session,
        histories: List[schemas.PlatformPriceHistoryCreate]
) -> OperationResult[int]:
    history_dicts = [history.model_dump() for history in histories]
    db.bulk_insert_mappings(models.PlatformPriceHistory, history_dicts)
    db.commit()
    return OperationResult(status=OperationStatus.SUCCESS, data=len(history_dicts))


def get_platform_price_histories(
        db: Session,
        page: int = 1,
        page_size: int = 100,
        platform_id: Optional[int] = None,
        appearance_id: Optional[int] = None
) -> OperationResult[List[schemas.PlatformPriceHistory]]:
    query = db.query(models.PlatformPriceHistory)

    if platform_id:
        query = query.filter(models.PlatformPriceHistory.platform_id == platform_id)
    if appearance_id:
        query = query.filter(models.PlatformPriceHistory.appearance_id == appearance_id)

    offset = (page - 1) * page_size
    db_platform_price_histories = query.offset(offset).limit(page_size).all()
    data = [schemas.PlatformPriceHistory.model_validate(db_platform_price_history) for db_platform_price_history in
            db_platform_price_histories]
    return OperationResult(status=OperationStatus.SUCCESS, data=data)


def delete_platform_price_history(db: Session, platform_price_history_id: int) -> OperationResult:
    db_platform_price_history = db.query(models.PlatformPriceHistory).filter(
        models.PlatformPriceHistory.id == platform_price_history_id).first()
    if not db_platform_price_history:
        return OperationResult(status=OperationStatus.NOT_FOUND)

    db.delete(db_platform_price_history)
    db.commit()

    return OperationResult(status=OperationStatus.SUCCESS)
