from fastapi import APIRouter, Depends, status
import logging
from sqlalchemy.orm import Session

import app.models as models
import app.schemas as schemas
from app.core.dependencies import require_admin
from app.core.exceptions import BusinessException
from app.core.operation_result import OperationStatus
from app.core.response import Response
from app.core.result_codes import ResultCode
from app.crud import crud_appearance_alias
from app.db.database import get_db

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("", status_code=status.HTTP_201_CREATED, response_model=Response[schemas.AppearanceAlias])
def create_appearance_alias(
        appearance_alias: schemas.AppearanceAliasCreate,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(require_admin)
):
    logger.info(f"User {current_user.email} is creating a new appearance alias: {appearance_alias.alias_name} for appearance {appearance_alias.appearance_id}")
    operation_result = crud_appearance_alias.create_appearance_alias(db=db, appearance_alias=appearance_alias)

    if operation_result.status == OperationStatus.CONFLICT:
        logger.warning(f"Appearance alias {appearance_alias.alias_name} already exists for appearance {appearance_alias.appearance_id}.")
        raise BusinessException(ResultCode.APPEARANCE_ALIAS_ALREADY_EXISTS)

    logger.info(f"Appearance alias created successfully with ID: {operation_result.data.id}")

    return Response(data=operation_result.data)


@router.put("/{alias_id}", response_model=Response[schemas.AppearanceAlias])
def update_appearance_alias(
        alias_id: int,
        appearance_alias: schemas.AppearanceAliasUpdate,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(require_admin)
):
    logger.info(f"User {current_user.email} is updating appearance alias with ID: {alias_id}")
    operation_result = crud_appearance_alias.update_appearance_alias(
        db,
        alias_id=alias_id,
        appearance_alias=appearance_alias
    )

    if operation_result.status == OperationStatus.CONFLICT:
        logger.warning(f"Appearance alias update failed due to conflict for alias ID: {alias_id}")
        raise BusinessException(ResultCode.APPEARANCE_ALIAS_ALREADY_EXISTS)
    elif operation_result.status == OperationStatus.NOT_FOUND:
        logger.warning(f"Appearance alias with ID {alias_id} not found for update.")
        raise BusinessException(ResultCode.NOT_FOUND)

    logger.info(f"Appearance alias with ID {alias_id} updated successfully.")

    return Response(data=operation_result.data)


@router.delete("/{alias_id}", response_model=Response)
def delete_appearance_alias(
        alias_id: int,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(require_admin)
):
    logger.info(f"User {current_user.email} is deleting appearance alias with ID: {alias_id}")
    operation_result = crud_appearance_alias.delete_appearance_alias(db, alias_id=alias_id)
    if operation_result.status == OperationStatus.NOT_FOUND:
        logger.warning(f"Appearance alias with ID {alias_id} not found for deletion.")
        raise BusinessException(ResultCode.NOT_FOUND)

    logger.info(f"Appearance alias with ID {alias_id} deleted successfully.")

    return Response(message="Appearance alias deleted successfully")
