from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import JWTError, jwt

from app.core.config import settings
from app.core.exceptions import BusinessException
from app.core.result_codes import ResultCode
from app.db.redis import redis_client


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(tz=timezone.utc) + expires_delta
    else:
        expire = datetime.now(tz=timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict):
    expire = datetime.now(tz=timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode = data.copy()
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

    # Store refresh token in Redis
    redis_client.set(f"refresh_token:{data['sub']}", encoded_jwt, ex=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS))

    return encoded_jwt


def verify_token(token: str):
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise BusinessException(ResultCode.INVALID_CREDENTIALS)
        return email
    except JWTError:
        raise BusinessException(ResultCode.INVALID_CREDENTIALS)


def revoke_refresh_token(email: str):
    redis_client.delete(f"refresh_token:{email}")
