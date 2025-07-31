from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.core.response import Response
from app.crud import crud_user_sale_transaction
from app.db.database import get_db
from app.models import User
from app.schemas import user_sale_transaction as user_sale_transaction_schema

router = APIRouter()


@router.post("", status_code=status.HTTP_201_CREATED,
             response_model=Response[user_sale_transaction_schema.UserSaleTransaction])
def create_user_sale_transaction(
        sale_transaction: user_sale_transaction_schema.UserSaleTransactionCreate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    new_sale_transaction = crud_user_sale_transaction.create_user_sale_transaction(
        db=db, user_id=current_user.id, sale_transaction=sale_transaction
    )
    return Response(data=new_sale_transaction)
