from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.core.operation_result import OperationResult, OperationStatus
from app.core.security import get_password_hash
from app.models import User
from app.schemas import UserCreate


def get_user_by_email(db: Session, email: str) -> OperationResult[User]:
    db_user = db.query(User).filter(User.email == email).first()
    if not db_user:
        return OperationResult(status=OperationStatus.NOT_FOUND)
    return OperationResult(status=OperationStatus.SUCCESS, data=db_user)


def create_user(db: Session, user: UserCreate) -> OperationResult[User]:
    hashed_password = get_password_hash(user.password)
    db_user = User(nickname=str(user.email).split('@')[0], email=str(user.email), password_hash=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return OperationResult(status=OperationStatus.SUCCESS, data=db_user)


def record_successful_login(db: Session, user: User) -> OperationResult:
    user.last_login_at = datetime.now(tz=timezone.utc)
    db.commit()
    return OperationResult(status=OperationStatus.SUCCESS)
