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


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    try:
        email = jwt_service.verify_token(token)
    except JWTError:
        raise BusinessException(ResultCode.INVALID_CREDENTIALS)
    user = crud_user.get_user_by_email(db, email=email)
    if user is None:
        raise BusinessException(ResultCode.INVALID_CREDENTIALS)
    return user


def require_admin(current_user: User = Depends(get_current_user)):
    if not current_user.is_admin:
        raise BusinessException(ResultCode.FORBIDDEN)
    if not current_user.is_active:
        raise BusinessException(ResultCode.INACTIVE_USER)
    return current_user
