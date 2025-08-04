from typing import List, Optional

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.dependencies import require_admin
from app.core.exceptions import BusinessException
from app.core.operation_result import OperationStatus
from app.core.response import Response
from app.core.result_codes import ResultCode
from app.crud import crud_appearance
from app.db.database import get_db
from app.models import User
from app.schemas import Appearance, AppearanceCreate, AppearanceUpdate

router = APIRouter()


@router.post("", status_code=status.HTTP_201_CREATED, response_model=Response[Appearance])
def create_appearance(
        appearance: AppearanceCreate,
        db: Session = Depends(get_db),
        _: User = Depends(require_admin)
):
    operation_result = crud_appearance.create_appearance(db=db, appearance=appearance)
    if operation_result.status == OperationStatus.CONFLICT:
        raise BusinessException(ResultCode.APPEARANCE_ALREADY_EXISTS)

    new_appearance = operation_result.data
    return Response(data=new_appearance)


@router.get("/{appearance_id}", response_model=Response[Appearance])
def get_appearance(
        appearance_id: int,
        db: Session = Depends(get_db),
        _: User = Depends(require_admin)
):
    db_appearance = crud_appearance.get_appearance_by_id(db, appearance_id=appearance_id)
    if db_appearance is None:
        raise BusinessException(ResultCode.NOT_FOUND)
    return Response(data=db_appearance)


@router.get("", response_model=Response[List[Appearance]])
def get_appearances(
        page: int = 1,
        page_size: int = 100,
        search_query: Optional[str] = None,
        db: Session = Depends(get_db),
        _: User = Depends(require_admin)
):
    appearances = crud_appearance.get_appearances(db, page=page, page_size=page_size, search_query=search_query)
    return Response(data=appearances)


@router.put("/{appearance_id}", response_model=Response[Appearance])
def update_appearance(
        appearance_id: int,
        appearance: AppearanceUpdate,
        db: Session = Depends(get_db),
        _: User = Depends(require_admin)
):
    operation_result = crud_appearance.update_appearance(db, appearance_id=appearance_id, appearance=appearance)
    if operation_result.status == OperationStatus.CONFLICT:
        raise BusinessException(ResultCode.APPEARANCE_ALREADY_EXISTS)
    elif operation_result.status == OperationStatus.NOT_FOUND:
        raise BusinessException(ResultCode.NOT_FOUND)

    return Response(data=operation_result.data)


@router.delete("/{appearance_id}", status_code=status.HTTP_204_NO_CONTENT, response_model=Response)
def delete_appearance(
        appearance_id: int,
        db: Session = Depends(get_db),
        _: User = Depends(require_admin)
):
    db_appearance = crud_appearance.delete_appearance(db, appearance_id=appearance_id)
    if db_appearance is None:
        raise BusinessException(ResultCode.NOT_FOUND)
    return Response(code=204, message="Appearance deleted successfully")
