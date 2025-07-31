from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.dependencies import require_admin
from app.core.exceptions import BusinessException
from app.core.response import Response
from app.core.result_codes import ResultCode
from app.crud import crud_platform
from app.db.database import get_db
from app.models import User
from app.schemas import platform as platform_schema

router = APIRouter()


@router.post("", status_code=status.HTTP_201_CREATED, response_model=Response[platform_schema.Platform])
def create_platform(
        platform: platform_schema.PlatformCreate,
        db: Session = Depends(get_db),
        _: User = Depends(require_admin)
):
    db_platform = crud_platform.get_platform_by_name(db, name=platform.name)
    if db_platform:
        raise BusinessException(ResultCode.PLATFORM_ALREADY_EXISTS)

    new_platform = crud_platform.create_platform(db=db, platform=platform)
    return Response(data=new_platform)
