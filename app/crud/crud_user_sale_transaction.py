from sqlalchemy.orm import Session

from app.models import UserSaleTransaction
from app.schemas import UserSaleTransactionCreate


def create_user_sale_transaction(db: Session, user_id: int,
                                 sale_transaction: UserSaleTransactionCreate) -> UserSaleTransaction:
    db_sale_transaction = UserSaleTransaction(
        user_id=user_id,
        **sale_transaction.model_dump()
    )
    db.add(db_sale_transaction)
    db.commit()
    db.refresh(db_sale_transaction)
    return db_sale_transaction
