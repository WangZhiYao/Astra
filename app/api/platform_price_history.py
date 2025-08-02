from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.dependencies import require_admin
from app.core.response import Response
from app.crud import crud_platform_price_history
from app.db.database import get_db
from app.models import User
from app.schemas import PlatformPriceHistoryCreate

router = APIRouter()


@router.post("", status_code=status.HTTP_201_CREATED)
def create_platform_price_histories(
        histories: List[PlatformPriceHistoryCreate],
        db: Session = Depends(get_db),
        _: User = Depends(require_admin)
):
    count = crud_platform_price_history.create_platform_price_histories(db=db, histories=histories)
    return Response(message=f"Successfully created {count} platform price histories.")
