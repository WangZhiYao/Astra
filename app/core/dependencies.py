import logging

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.orm import Session

from app.core.exceptions import BusinessException
from app.core.result_codes import ResultCode
from app.crud import crud_user
from app.db.database import get_db
from app.models import User
from app.services import jwt_service

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")
logger = logging.getLogger(__name__)


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    try:
        email = jwt_service.verify_token(token)
    except JWTError as e:
        logger.warning(f"JWTError while verifying token: {e}")
        raise BusinessException(ResultCode.INVALID_CREDENTIALS)
    user = crud_user.get_user_by_email(db, email=email)
    if user is None:
        logger.warning(f"User not found for email: {email} from token")
        raise BusinessException(ResultCode.INVALID_CREDENTIALS)
    return user


def require_admin(current_user: User = Depends(get_current_user)):
    if not current_user.is_admin:
        logger.warning(f"User {current_user.email} attempted to access an admin-only endpoint.")
        raise BusinessException(ResultCode.FORBIDDEN)
    if not current_user.is_active:
        logger.warning(f"Inactive admin user {current_user.email} attempted to access an endpoint.")
        raise BusinessException(ResultCode.INACTIVE_USER)
    return current_user
