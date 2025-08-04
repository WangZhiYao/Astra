from typing import List, Optional

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.dependencies import require_admin
from app.core.exceptions import BusinessException
from app.core.response import Response
from app.core.result_codes import ResultCode
from app.crud import crud_platform_price_history
from app.db.database import get_db
from app.models import User
from app.schemas import PlatformPriceHistoryCreate, PlatformPriceHistory

router = APIRouter()


@router.post("", status_code=status.HTTP_201_CREATED)
def create_platform_price_histories(
        histories: List[PlatformPriceHistoryCreate],
        db: Session = Depends(get_db),
        _: User = Depends(require_admin)
):
    count = crud_platform_price_history.create_platform_price_histories(db=db, histories=histories)
    return Response(message=f"Successfully created {count} platform price histories.")


@router.get("", response_model=Response[List[PlatformPriceHistory]])
def get_platform_price_histories(
        page: int = 1,
        page_size: int = 100,
        platform_id: Optional[int] = None,
        appearance_id: Optional[int] = None,
        db: Session = Depends(get_db)
):
    histories = crud_platform_price_history.get_platform_price_histories(
        db,
        page=page,
        page_size=page_size,
        platform_id=platform_id,
        appearance_id=appearance_id
    )
    return Response(data=histories)


@router.delete("/{history_id}", status_code=status.HTTP_204_NO_CONTENT, response_model=Response)
def delete_platform_price_history(
        history_id: int,
        db: Session = Depends(get_db),
        _: User = Depends(require_admin)
):
    db_history = crud_platform_price_history.delete_platform_price_history(db, history_id=history_id)
    if db_history is None:
        raise BusinessException(ResultCode.NOT_FOUND)
    return Response(code=204, message="Platform price history deleted successfully")
