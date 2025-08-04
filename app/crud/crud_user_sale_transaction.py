from datetime import datetime
from typing import List, Optional

from sqlalchemy.orm import Session

from app.core.operation_result import OperationResult, OperationStatus
from app.models import UserSaleTransaction
from app.schemas import UserSaleTransactionCreate, UserSaleTransactionUpdate


def create_user_sale_transaction(
        db: Session,
        user_id: int,
        sale_transaction: UserSaleTransactionCreate
) -> UserSaleTransaction:
    db_sale_transaction = UserSaleTransaction(user_id=user_id, **sale_transaction.model_dump())
    db.add(db_sale_transaction)
    db.commit()
    db.refresh(db_sale_transaction)
    return db_sale_transaction


def get_user_sale_transaction_by_id(db: Session, user_id: int, transaction_id: int):
    return db.query(UserSaleTransaction).filter(
        UserSaleTransaction.user_id == user_id,
        UserSaleTransaction.id == transaction_id
    ).first()


def get_user_sale_transactions(
        db: Session,
        user_id: int,
        page: int = 1,
        page_size: int = 100,
        appearance_id: Optional[int] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
) -> List[UserSaleTransaction]:
    query = db.query(UserSaleTransaction).filter(UserSaleTransaction.user_id == user_id)

    if appearance_id:
        query = query.filter(UserSaleTransaction.appearance_id == appearance_id)
    if start_date:
        query = query.filter(UserSaleTransaction.sold_at >= start_date)
    if end_date:
        query = query.filter(UserSaleTransaction.sold_at <= end_date)

    offset = (page - 1) * page_size
    return query.offset(offset).limit(page_size).all()


def update_user_sale_transaction(
        db: Session,
        user_id: int,
        transaction_id: int,
        transaction: UserSaleTransactionUpdate
) -> OperationResult[UserSaleTransaction]:
    db_transaction = get_user_sale_transaction_by_id(db=db, user_id=user_id, transaction_id=transaction_id)
    if not db_transaction:
        return OperationResult(status=OperationStatus.NOT_FOUND)

    update_data = transaction.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_transaction, key, value)
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)

    return OperationResult(status=OperationStatus.SUCCESS, data=db_transaction)


def delete_user_sale_transaction(db: Session, user_id: int, transaction_id: int):
    db_transaction = get_user_sale_transaction_by_id(db=db, user_id=user_id, transaction_id=transaction_id)
    if not db_transaction:
        return OperationResult(status=OperationStatus.NOT_FOUND)

    db.delete(db_transaction)
    db.commit()

    return OperationResult(status=OperationStatus.SUCCESS, data=db_transaction)
