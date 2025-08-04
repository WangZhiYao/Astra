import logging
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.core.exceptions import BusinessException
from app.core.operation_result import OperationStatus
from app.core.response import Response
from app.core.result_codes import ResultCode
from app.crud import crud_user_sale_transaction
from app.db.database import get_db
from app.models import User
from app.schemas import user_sale_transaction as user_sale_transaction_schema

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("", status_code=status.HTTP_201_CREATED,
             response_model=Response[user_sale_transaction_schema.UserSaleTransaction])
def create_user_sale_transaction(
        sale_transaction: user_sale_transaction_schema.UserSaleTransactionCreate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    logger.info(f"User {current_user.email} is creating a new sale transaction.")
    new_sale_transaction = crud_user_sale_transaction.create_user_sale_transaction(
        db=db,
        user_id=current_user.id,
        sale_transaction=sale_transaction
    )
    logger.info(f"Sale transaction {new_sale_transaction.id} created successfully for user {current_user.email}.")
    return Response(data=new_sale_transaction)


@router.get("/{transaction_id}", response_model=Response[user_sale_transaction_schema.UserSaleTransaction])
def get_user_sale_transaction(
        transaction_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    db_transaction = crud_user_sale_transaction.get_user_sale_transaction_by_id(
        db=db,
        user_id=current_user.id,
        transaction_id=transaction_id
    )

    if not db_transaction:
        raise BusinessException(ResultCode.NOT_FOUND)

    return Response(data=db_transaction)


@router.get("", response_model=Response[List[user_sale_transaction_schema.UserSaleTransaction]])
def get_user_sale_transactions(
        page: int = 1,
        page_size: int = 100,
        appearance_id: Optional[int] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    transactions = crud_user_sale_transaction.get_user_sale_transactions(
        db=db,
        user_id=current_user.id,
        page=page,
        page_size=page_size,
        appearance_id=appearance_id,
        start_date=start_date,
        end_date=end_date
    )

    return Response(data=transactions)


@router.put("/{transaction_id}", response_model=Response[user_sale_transaction_schema.UserSaleTransaction])
def update_user_sale_transaction(
        transaction_id: int,
        transaction: user_sale_transaction_schema.UserSaleTransactionUpdate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    operation_result = crud_user_sale_transaction.update_user_sale_transaction(
        db=db,
        user_id=current_user.id,
        transaction_id=transaction_id,
        transaction=transaction
    )

    if operation_result.status == OperationStatus.NOT_FOUND:
        raise BusinessException(ResultCode.NOT_FOUND)

    return Response(data=operation_result.data)


@router.delete("/{transaction_id}", response_model=Response)
def delete_user_sale_transaction(
        transaction_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    operation_result = crud_user_sale_transaction.delete_user_sale_transaction(
        db=db,
        user_id=current_user.id,
        transaction_id=transaction_id
    )

    if operation_result.status == OperationStatus.NOT_FOUND:
        raise BusinessException(ResultCode.NOT_FOUND)

    return Response(message="Sale transaction deleted successfully")
