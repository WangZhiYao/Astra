from datetime import datetime, timezone

from sqlalchemy.orm import Session

import app.models as models
import app.schemas as schemas
from app.core.security import get_password_hash


def get_user_by_email(db: Session, email: str) -> models.User | None:
    """Fetches a user by email from the database."""
    return db.query(models.User).filter(models.User.email == email).first()


def create_user(db: Session, user: schemas.UserCreate) -> models.User:
    """Creates a new user in the database."""
    hashed_password = get_password_hash(user.password)
    db_user = models.User(nickname=str(user.email).split('@')[0], email=str(user.email), password_hash=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def update_user_login_timestamp(db: Session, db_user: models.User) -> models.User:
    """Updates the last_login_at timestamp for a given user instance."""
    db_user.last_login_at = datetime.now(tz=timezone.utc)
    # The service layer will handle the commit.
    db.add(db_user)
    return db_user
