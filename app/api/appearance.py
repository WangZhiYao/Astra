from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.dependencies import require_admin
from app.core.exceptions import BusinessException
from app.core.response import Response
from app.core.result_codes import ResultCode
from app.crud import crud_appearance
from app.db.database import get_db
from app.models import User
from app.schemas import appearance as appearance_schema

router = APIRouter()


@router.post("", status_code=status.HTTP_201_CREATED, response_model=Response[appearance_schema.Appearance])
def create_appearance(
        appearance: appearance_schema.AppearanceCreate,
        db: Session = Depends(get_db),
        _: User = Depends(require_admin)
):
    db_appearance = crud_appearance.get_appearance_by_name(db, name=appearance.name)
    if db_appearance:
        raise BusinessException(ResultCode.APPEARANCE_ALREADY_EXISTS)

    new_appearance = crud_appearance.create_appearance(db=db, appearance=appearance)
    return Response(data=new_appearance)
