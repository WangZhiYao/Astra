from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.dependencies import require_admin
from app.core.exceptions import BusinessException
from app.core.response import Response
from app.core.result_codes import ResultCode
from app.crud import crud_appearance_alias
from app.db.database import get_db
from app.models import User
from app.schemas import appearance_alias as appearance_alias_schema

router = APIRouter()


@router.post("", status_code=status.HTTP_201_CREATED, response_model=Response[appearance_alias_schema.AppearanceAlias])
def create_appearance_type(
        appearance_alias: appearance_alias_schema.AppearanceAliasCreate,
        db: Session = Depends(get_db),
        _: User = Depends(require_admin)
):
    db_appearance_alias = crud_appearance_alias.get_appearance_alias_by_alias_name(db,
                                                                                   appearance_id=appearance_alias.appearance_id,
                                                                                   alias_name=appearance_alias.alias_name)
    if db_appearance_alias:
        raise BusinessException(ResultCode.APPEARANCE_ALIAS_ALREADY_EXISTS)

    new_appearance_alias = crud_appearance_alias.create_appearance_alias(db=db, appearance_alias=appearance_alias)
    return Response(data=new_appearance_alias)
