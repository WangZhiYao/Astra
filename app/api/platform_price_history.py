import logging
from typing import List, Optional

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.dependencies import require_admin
from app.core.exceptions import BusinessException
from app.core.operation_result import OperationStatus
from app.core.response import Response
from app.core.result_codes import ResultCode
from app.crud import crud_platform_price_history
from app.db.database import get_db
from app.models import User
from app.schemas import PlatformPriceHistoryCreate, PlatformPriceHistory

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("", status_code=status.HTTP_201_CREATED)
def create_platform_price_histories(
        histories: List[PlatformPriceHistoryCreate],
        db: Session = Depends(get_db),
        current_user: User = Depends(require_admin)
):
    logger.info(f"User {current_user.email} is creating {len(histories)} new platform price histories.")
    operation_result = crud_platform_price_history.create_platform_price_histories(db=db, histories=histories)
    logger.info(f"Successfully created {operation_result.data} platform price histories.")
    return Response(message=f"Successfully created {operation_result.data} platform price histories.")


@router.get("", response_model=Response[List[PlatformPriceHistory]])
def get_platform_price_histories(
        page: int = 1,
        page_size: int = 100,
        platform_id: Optional[int] = None,
        appearance_id: Optional[int] = None,
        db: Session = Depends(get_db)
):
    logger.info(f"Fetching platform price histories with page: {page}, page_size: {page_size}, platform_id: {platform_id}, appearance_id: {appearance_id}")
    operation_result = crud_platform_price_history.get_platform_price_histories(
        db,
        page=page,
        page_size=page_size,
        platform_id=platform_id,
        appearance_id=appearance_id
    )
    logger.info(f"Found {len(operation_result.data)} platform price histories.")
    return Response(data=operation_result.data)


@router.delete("/{platform_price_history_id}", response_model=Response)
def delete_platform_price_history(
        platform_price_history_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(require_admin)
):
    logger.info(f"User {current_user.email} is deleting platform price history with ID: {platform_price_history_id}")
    operation_result = crud_platform_price_history.delete_platform_price_history(
        db=db,
        platform_price_history_id=platform_price_history_id
    )
    if operation_result.status == OperationStatus.NOT_FOUND:
        logger.warning(f"Platform price history with ID {platform_price_history_id} not found for deletion.")
        raise BusinessException(ResultCode.NOT_FOUND)
    logger.info(f"Platform price history with ID {platform_price_history_id} deleted successfully.")
    return Response(message="Platform price history deleted successfully")
