import logging

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.core.response import Response
from app.crud import crud_user_stats
from app.db.database import get_db
from app.models import User
from app.schemas import UserStats

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/stats", response_model=Response[UserStats])
def get_user_stats(
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    logger.info(f"User {current_user.email} is fetching their stats.")
    operation_result = crud_user_stats.get_user_stats(db, user_id=current_user.id)
    logger.info(f"User {current_user.email} stats fetched successfully.")
    return Response(data=operation_result.data)
