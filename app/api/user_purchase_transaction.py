import logging

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.core.response import Response
from app.crud import crud_user_purchase_transaction
from app.db.database import get_db
from app.models import User
from app.schemas import user_purchase_transaction as user_purchase_transaction_schema

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("", status_code=status.HTTP_201_CREATED,
             response_model=Response[user_purchase_transaction_schema.UserPurchaseTransaction])
def create_user_purchase_transaction(
        purchase_transaction: user_purchase_transaction_schema.UserPurchaseTransactionCreate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    logger.info(f"User {current_user.email} is creating a new purchase transaction.")
    new_purchase_transaction = crud_user_purchase_transaction.create_user_purchase_transaction(
        db=db, user_id=current_user.id, purchase_transaction=purchase_transaction
    )
    logger.info(f"Purchase transaction {new_purchase_transaction.id} created successfully for user {current_user.email}.")
    return Response(data=new_purchase_transaction)
