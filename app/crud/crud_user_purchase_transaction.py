from sqlalchemy.orm import Session

from app.models import UserPurchaseTransaction
from app.schemas import UserPurchaseTransactionCreate


def create_user_purchase_transaction(db: Session, user_id: int,
                                     purchase_transaction: UserPurchaseTransactionCreate) -> UserPurchaseTransaction:
    db_purchase_transaction = UserPurchaseTransaction(
        user_id=user_id,
        **purchase_transaction.model_dump()
    )
    db.add(db_purchase_transaction)
    db.commit()
    db.refresh(db_purchase_transaction)
    return db_purchase_transaction
