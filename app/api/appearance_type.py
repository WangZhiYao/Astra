from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.dependencies import require_admin
from app.core.exceptions import BusinessException
from app.core.operation_result import OperationStatus
from app.core.response import Response
from app.core.result_codes import ResultCode
from app.crud import crud_appearance_type
from app.db.database import get_db
from app.models import User
from app.schemas import AppearanceType, AppearanceTypeCreate, AppearanceTypeUpdate

router = APIRouter()


@router.post("", status_code=status.HTTP_201_CREATED, response_model=Response[AppearanceType])
def create_appearance_type(
        appearance_type: AppearanceTypeCreate,
        db: Session = Depends(get_db),
        _: User = Depends(require_admin)
):
    operation_result = crud_appearance_type.create_appearance_type(db, appearance_type=appearance_type)
    if operation_result.status == OperationStatus.CONFLICT:
        raise BusinessException(ResultCode.APPEARANCE_TYPE_ALREADY_EXISTS)

    return Response(data=operation_result.data)


@router.get("", response_model=Response[List[AppearanceType]])
def get_appearance_types(
        page: int = 1,
        page_size: int = 100,
        db: Session = Depends(get_db)
):
    appearance_types = crud_appearance_type.get_appearance_types(db, page=page, page_size=page_size)
    return Response(data=appearance_types)


@router.put("/{type_id}", response_model=Response[AppearanceType])
def update_appearance_type(
        type_id: int,
        appearance_type: AppearanceTypeUpdate,
        db: Session = Depends(get_db),
        _: User = Depends(require_admin)
):
    db_appearance_type = crud_appearance_type.update_appearance_type(
        db,
        type_id=type_id,
        appearance_type=appearance_type
    )
    if db_appearance_type is None:
        raise BusinessException(ResultCode.NOT_FOUND)
    return Response(data=db_appearance_type)


@router.delete("/{type_id}", status_code=status.HTTP_204_NO_CONTENT, response_model=Response)
def delete_appearance_type(
        type_id: int,
        db: Session = Depends(get_db),
        _: User = Depends(require_admin)
):
    db_appearance_type = crud_appearance_type.delete_appearance_type(db, type_id=type_id)
    if db_appearance_type is None:
        raise BusinessException(ResultCode.NOT_FOUND)
    return Response(code=204, message="Appearance type deleted successfully")
