from datetime import datetime
from typing import List, Optional

from sqlalchemy.orm import Session

from app.core.operation_result import OperationResult, OperationStatus
from app.models import UserPurchaseTransaction
from app.schemas import UserPurchaseTransactionCreate, UserPurchaseTransactionUpdate


def create_user_purchase_transaction(
        db: Session,
        user_id: int,
        purchase_transaction: UserPurchaseTransactionCreate
) -> UserPurchaseTransaction:
    db_purchase_transaction = UserPurchaseTransaction(user_id=user_id, **purchase_transaction.model_dump())
    db.add(db_purchase_transaction)
    db.commit()
    db.refresh(db_purchase_transaction)
    return db_purchase_transaction


def get_user_purchase_transaction_by_id(db: Session, user_id: int, transaction_id: int):
    return db.query(UserPurchaseTransaction).filter(
        UserPurchaseTransaction.user_id == user_id,
        UserPurchaseTransaction.id == transaction_id
    ).first()


def get_user_purchase_transactions(
        db: Session,
        user_id: int,
        page: int = 1,
        page_size: int = 100,
        appearance_id: Optional[int] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
) -> List[UserPurchaseTransaction]:
    query = db.query(UserPurchaseTransaction).filter(UserPurchaseTransaction.user_id == user_id)

    if appearance_id:
        query = query.filter(UserPurchaseTransaction.appearance_id == appearance_id)
    if start_date:
        query = query.filter(UserPurchaseTransaction.purchased_at >= start_date)
    if end_date:
        query = query.filter(UserPurchaseTransaction.purchased_at <= end_date)

    offset = (page - 1) * page_size
    return query.offset(offset).limit(page_size).all()


def update_user_purchase_transaction(
        db: Session,
        user_id: int,
        transaction_id: int,
        transaction: UserPurchaseTransactionUpdate
) -> OperationResult[UserPurchaseTransaction]:
    db_transaction = get_user_purchase_transaction_by_id(db=db, user_id=user_id, transaction_id=transaction_id)
    if not db_transaction:
        return OperationResult(status=OperationStatus.NOT_FOUND)

    update_data = transaction.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_transaction, key, value)
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)

    return OperationResult(status=OperationStatus.SUCCESS, data=db_transaction)


def delete_user_purchase_transaction(db: Session, user_id: int, transaction_id: int):
    db_transaction = get_user_purchase_transaction_by_id(db=db, user_id=user_id, transaction_id=transaction_id)
    if not db_transaction:
        return OperationResult(status=OperationStatus.NOT_FOUND)

    db.delete(db_transaction)
    db.commit()

    return OperationResult(status=OperationStatus.SUCCESS, data=db_transaction)
