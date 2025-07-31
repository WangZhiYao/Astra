from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.dependencies import require_admin
from app.core.exceptions import BusinessException
from app.core.response import Response
from app.core.result_codes import ResultCode
from app.crud import crud_appearance_type
from app.db.database import get_db
from app.models import User
from app.schemas import appearance_type as appearance_type_schema

router = APIRouter()


@router.post("", status_code=status.HTTP_201_CREATED, response_model=Response[appearance_type_schema.AppearanceType])
def create_appearance_type(
        appearance_type: appearance_type_schema.AppearanceTypeCreate,
        db: Session = Depends(get_db),
        _: User = Depends(require_admin)
):
    db_appearance_type = crud_appearance_type.get_appearance_type_by_name(db, name=appearance_type.name)
    if db_appearance_type:
        raise BusinessException(ResultCode.APPEARANCE_TYPE_ALREADY_EXISTS)

    new_appearance_type = crud_appearance_type.create_appearance_type(db=db, appearance_type=appearance_type)
    return Response(data=new_appearance_type)
