import logging
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

import app.models as models
import app.schemas as schemas
from app.core.dependencies import get_current_user
from app.core.exceptions import BusinessException
from app.core.operation_result import OperationStatus
from app.core.response import Response
from app.core.result_codes import ResultCode
from app.crud import crud_user_purchase_transaction
from app.db.database import get_db

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("", status_code=status.HTTP_201_CREATED,
             response_model=Response[schemas.UserPurchaseTransaction])
def create_user_purchase_transaction(
        purchase_transaction: schemas.UserPurchaseTransactionCreate,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(get_current_user)
):
    logger.info(f"User {current_user.email} is creating a new purchase transaction.")
    new_purchase_transaction = crud_user_purchase_transaction.create_user_purchase_transaction(
        db=db,
        user_id=current_user.id,
        purchase_transaction=purchase_transaction
    )
    logger.info(
        f"Purchase transaction {new_purchase_transaction.id} created successfully for user {current_user.email}.")
    return Response(data=new_purchase_transaction)


@router.get("/{transaction_id}", response_model=Response[schemas.UserPurchaseTransaction])
def get_user_purchase_transaction(
        transaction_id: int,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(get_current_user)
):
    db_transaction = crud_user_purchase_transaction.get_user_purchase_transaction_by_id(
        db=db,
        user_id=current_user.id,
        transaction_id=transaction_id
    )

    if not db_transaction:
        raise BusinessException(ResultCode.NOT_FOUND)

    return Response(data=schemas.UserPurchaseTransaction.model_validate(db_transaction))


@router.get("", response_model=Response[List[schemas.UserPurchaseTransaction]])
def get_user_purchase_transactions(
        page: int = 1,
        page_size: int = 100,
        appearance_id: Optional[int] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(get_current_user)
):
    transactions = crud_user_purchase_transaction.get_user_purchase_transactions(
        db=db,
        user_id=current_user.id,
        page=page,
        page_size=page_size,
        appearance_id=appearance_id,
        start_date=start_date,
        end_date=end_date
    )

    return Response(data=transactions)


@router.put("/{transaction_id}", response_model=Response[schemas.UserPurchaseTransaction])
def update_user_purchase_transaction(
        transaction_id: int,
        transaction: schemas.UserPurchaseTransactionUpdate,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(get_current_user)
):
    operation_result = crud_user_purchase_transaction.update_user_purchase_transaction(
        db=db,
        user_id=current_user.id,
        transaction_id=transaction_id,
        transaction=transaction
    )

    if operation_result.status == OperationStatus.NOT_FOUND:
        raise BusinessException(ResultCode.NOT_FOUND)

    return Response(data=operation_result.data)


@router.delete("/{transaction_id}", response_model=Response)
def delete_user_purchase_transaction(
        transaction_id: int,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(get_current_user)
):
    operation_result = crud_user_purchase_transaction.delete_user_purchase_transaction(
        db=db,
        user_id=current_user.id,
        transaction_id=transaction_id
    )

    if operation_result.status == OperationStatus.NOT_FOUND:
        raise BusinessException(ResultCode.NOT_FOUND)

    return Response(message="Purchase transaction deleted successfully")
