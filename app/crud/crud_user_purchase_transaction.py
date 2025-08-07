from datetime import datetime
from typing import List, Optional

from sqlalchemy.orm import Session, joinedload

import app.models as models
import app.schemas as schemas
from app.core.operation_result import OperationResult, OperationStatus


def create_user_purchase_transaction(
        db: Session,
        user_id: int,
        purchase_transaction: schemas.UserPurchaseTransactionCreate
) -> OperationResult[schemas.UserPurchaseTransaction]:
    db_purchase_transaction = models.UserPurchaseTransaction(user_id=user_id, **purchase_transaction.model_dump())
    db.add(db_purchase_transaction)
    db.commit()
    db.refresh(db_purchase_transaction)
    return OperationResult(
        status=OperationStatus.SUCCESS,
        data=schemas.UserPurchaseTransaction.model_validate(db_purchase_transaction)
    )


def get_user_purchase_transaction_by_id(
        db: Session,
        user_id: int,
        transaction_id: int
) -> OperationResult[schemas.UserPurchaseTransaction]:
    db_transaction = db.query(models.UserPurchaseTransaction).options(
        joinedload(models.UserPurchaseTransaction.appearance),
        joinedload(models.UserPurchaseTransaction.platform)
    ).filter(
        models.UserPurchaseTransaction.user_id == user_id,
        models.UserPurchaseTransaction.id == transaction_id
    ).first()
    if not db_transaction:
        return OperationResult(status=OperationStatus.NOT_FOUND)
    return OperationResult(status=OperationStatus.SUCCESS,
                           data=schemas.UserPurchaseTransaction.model_validate(db_transaction))


def get_user_purchase_transactions(
        db: Session,
        user_id: int,
        page: int = 1,
        page_size: int = 100,
        appearance_id: Optional[int] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
) -> OperationResult[List[schemas.UserPurchaseTransaction]]:
    query = db.query(models.UserPurchaseTransaction).options(
        joinedload(models.UserPurchaseTransaction.appearance),
        joinedload(models.UserPurchaseTransaction.platform)
    ).filter(models.UserPurchaseTransaction.user_id == user_id)

    if appearance_id:
        query = query.filter(models.UserPurchaseTransaction.appearance_id == appearance_id)
    if start_date:
        query = query.filter(models.UserPurchaseTransaction.purchased_at >= start_date)
    if end_date:
        query = query.filter(models.UserPurchaseTransaction.purchased_at <= end_date)

    offset = (page - 1) * page_size
    db_purchase_transactions = query.offset(offset).limit(page_size).all()
    data = [schemas.UserPurchaseTransaction.model_validate(db_purchase_transaction) for db_purchase_transaction in
            db_purchase_transactions]
    return OperationResult(status=OperationStatus.SUCCESS, data=data)


def update_user_purchase_transaction(
        db: Session,
        user_id: int,
        transaction_id: int,
        transaction: schemas.UserPurchaseTransactionUpdate
) -> OperationResult[schemas.UserPurchaseTransaction]:
    db_transaction = get_user_purchase_transaction_by_id(db=db, user_id=user_id, transaction_id=transaction_id).data
    if not db_transaction:
        return OperationResult(status=OperationStatus.NOT_FOUND)

    update_data = transaction.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_transaction, key, value)
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)

    return OperationResult(
        status=OperationStatus.SUCCESS,
        data=schemas.UserPurchaseTransaction.model_validate(db_transaction)
    )


def delete_user_purchase_transaction(db: Session, user_id: int, transaction_id: int) -> OperationResult:
    db_transaction = get_user_purchase_transaction_by_id(db=db, user_id=user_id, transaction_id=transaction_id).data
    if not db_transaction:
        return OperationResult(status=OperationStatus.NOT_FOUND)

    db.delete(db_transaction)
    db.commit()

    return OperationResult(status=OperationStatus.SUCCESS)
