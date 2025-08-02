import logging

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.exceptions import BusinessException
from app.core.response import Response
from app.core.result_codes import ResultCode
from app.core.security import verify_password
from app.crud import crud_user
from app.db.database import get_db
from app.db.redis import redis_client
from app.schemas import user as user_schema, token as token_schema
from app.schemas.token import TokenRefreshRequest
from app.services import jwt_service

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/register", status_code=status.HTTP_201_CREATED, response_model=Response[token_schema.Token])
def register(user: user_schema.UserCreate, db: Session = Depends(get_db)):
    logger.info(f"Registering user with email: {user.email}")
    db_user = crud_user.get_user_by_email(db, email=str(user.email))
    if db_user:
        logger.warning(f"Email {user.email} already registered.")
        raise BusinessException(ResultCode.EMAIL_ALREADY_REGISTERED)

    new_user = crud_user.create_user(db=db, user=user)
    logger.info(f"User {new_user.email} registered successfully.")

    access_token = jwt_service.create_access_token(data={"sub": new_user.email})
    refresh_token = jwt_service.create_refresh_token(data={"sub": new_user.email})

    return Response(
        data=token_schema.Token(access_token=access_token, refresh_token=refresh_token, token_type="bearer")
    )


@router.post("/login", response_model=Response[token_schema.Token])
def login(user: user_schema.UserLogin, db: Session = Depends(get_db)):
    logger.info(f"Login attempt for user: {user.email}")
    db_user = crud_user.get_user_by_email(db, email=str(user.email))
    if db_user:
        if not db_user.is_active:
            logger.warning(f"Login failed for inactive user: {user.email}")
            raise BusinessException(ResultCode.INACTIVE_USER)

        login_attempts_key = f"failed_login_attempts:{db_user.email}"
        login_attempts = redis_client.get(login_attempts_key)
        if login_attempts and int(login_attempts) >= settings.MAX_LOGIN_ATTEMPTS:
            logger.warning(f"Too many login attempts for user: {user.email}")
            raise BusinessException(ResultCode.TOO_MANY_LOGIN_ATTEMPTS)

    if not db_user or not verify_password(user.password, db_user.password_hash):
        if db_user:
            login_attempts_key = f"failed_login_attempts:{db_user.email}"
            redis_client.incr(login_attempts_key)
            if redis_client.ttl(login_attempts_key) == -1:
                redis_client.expire(login_attempts_key, settings.LOGIN_ATTEMPT_WINDOW_MINUTES * 60)
            logger.warning(f"Invalid password for user: {user.email}")
        else:
            logger.warning(f"Login failed for non-existent user: {user.email}")
        raise BusinessException(ResultCode.LOGIN_FAILED)

    crud_user.record_successful_login(db, db_user)
    redis_client.delete(f"failed_login_attempts:{db_user.email}")
    logger.info(f"User {db_user.email} logged in successfully.")

    access_token = jwt_service.create_access_token(data={"sub": db_user.email})
    refresh_token = jwt_service.create_refresh_token(data={"sub": db_user.email})

    return Response(
        data=token_schema.Token(access_token=access_token, refresh_token=refresh_token, token_type="bearer")
    )


@router.post("/refresh", response_model=Response[token_schema.Token])
def refresh_token(request: TokenRefreshRequest, db: Session = Depends(get_db)):
    logger.info("Attempting to refresh token.")
    email = jwt_service.verify_token(request.refresh_token)

    # Check if refresh token is valid (exists in Redis)
    stored_token = jwt_service.redis_client.get(f"refresh_token:{email}")
    if not stored_token or stored_token.decode('utf-8') != request.refresh_token:
        logger.warning(f"Invalid refresh token for email: {email}")
        raise BusinessException(ResultCode.INVALID_REFRESH_TOKEN)

    user = crud_user.get_user_by_email(db, email=email)
    if user is None:
        logger.error(f"User not found for email: {email} during token refresh.")
        raise BusinessException(ResultCode.INVALID_CREDENTIALS)

    access_token = jwt_service.create_access_token(data={"sub": user.email})
    new_refresh_token = jwt_service.create_refresh_token(data={"sub": user.email})
    logger.info(f"Token refreshed successfully for user: {user.email}")

    return Response(
        data=token_schema.Token(access_token=access_token, refresh_token=new_refresh_token, token_type="bearer")
    )
