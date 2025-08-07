import logging

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

import app.models as models
import app.schemas as schemas
from app.core.dependencies import get_current_user
from app.core.response import Response
from app.crud import crud_user_stats
from app.db.database import get_db

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/stats", response_model=Response[schemas.UserStats])
def get_user_stats(
        db: Session = Depends(get_db),
        current_user: models.User = Depends(get_current_user)
):
    logger.info(f"User {current_user.email} is fetching their stats.")
    operation_result = crud_user_stats.get_user_stats(db, user_id=current_user.id)
    logger.info(f"User {current_user.email} stats fetched successfully.")
    return Response(data=operation_result.data)
