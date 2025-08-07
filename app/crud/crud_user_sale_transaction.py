from datetime import datetime
from typing import List, Optional

from sqlalchemy.orm import Session, joinedload

import app.models as models
import app.schemas as schemas
from app.core.operation_result import OperationResult, OperationStatus


def create_user_sale_transaction(
        db: Session,
        user_id: int,
        sale_transaction: schemas.UserSaleTransactionCreate
) -> OperationResult[schemas.UserSaleTransaction]:
    db_sale_transaction = models.UserSaleTransaction(user_id=user_id, **sale_transaction.model_dump())
    db.add(db_sale_transaction)
    db.commit()
    db.refresh(db_sale_transaction)
    return OperationResult(
        status=OperationStatus.SUCCESS,
        data=schemas.UserSaleTransaction.model_validate(db_sale_transaction)
    )


def get_user_sale_transaction_by_id(
        db: Session,
        user_id: int,
        transaction_id: int
) -> OperationResult[schemas.UserSaleTransaction]:
    db_transaction = db.query(models.UserSaleTransaction).options(
        joinedload(models.UserSaleTransaction.appearance),
        joinedload(models.UserSaleTransaction.platform)
    ).filter(
        models.UserSaleTransaction.user_id == user_id,
        models.UserSaleTransaction.id == transaction_id
    ).first()

    if not db_transaction:
        return OperationResult(status=OperationStatus.NOT_FOUND)

    return OperationResult(
        status=OperationStatus.SUCCESS,
        data=schemas.UserSaleTransaction.model_validate(db_transaction)
    )


def get_user_sale_transactions(
        db: Session,
        user_id: int,
        page: int = 1,
        page_size: int = 100,
        appearance_id: Optional[int] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
) -> OperationResult[List[schemas.UserSaleTransaction]]:
    query = db.query(models.UserSaleTransaction).options(
        joinedload(models.UserSaleTransaction.appearance),
        joinedload(models.UserSaleTransaction.platform)
    ).filter(models.UserSaleTransaction.user_id == user_id)

    if appearance_id:
        query = query.filter(models.UserSaleTransaction.appearance_id == appearance_id)
    if start_date:
        query = query.filter(models.UserSaleTransaction.sold_at >= start_date)
    if end_date:
        query = query.filter(models.UserSaleTransaction.sold_at <= end_date)

    offset = (page - 1) * page_size
    db_sale_transactions = query.offset(offset).limit(page_size).all()
    data = [schemas.UserSaleTransaction.model_validate(db_sale_transaction) for db_sale_transaction in
            db_sale_transactions]
    return OperationResult(status=OperationStatus.SUCCESS, data=data)


def update_user_sale_transaction(
        db: Session,
        user_id: int,
        transaction_id: int,
        transaction: schemas.UserSaleTransactionUpdate
) -> OperationResult[schemas.UserSaleTransaction]:
    db_transaction = db.query(models.UserSaleTransaction).filter(
        models.UserSaleTransaction.user_id == user_id,
        models.UserSaleTransaction.id == transaction_id
    ).first()

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
        data=schemas.UserSaleTransaction.model_validate(db_transaction)
    )


def delete_user_sale_transaction(db: Session, user_id: int, transaction_id: int) -> OperationResult:
    db_transaction = db.query(models.UserSaleTransaction).filter(
        models.UserSaleTransaction.user_id == user_id,
        models.UserSaleTransaction.id == transaction_id
    ).first()

    if not db_transaction:
        return OperationResult(status=OperationStatus.NOT_FOUND)

    db.delete(db_transaction)
    db.commit()

    return OperationResult(status=OperationStatus.SUCCESS)
