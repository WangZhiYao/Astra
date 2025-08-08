import logging

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

import app.schemas as schemas
from app.core.exceptions import BusinessException
from app.core.response import Response
from app.core.result_codes import ResultCode
from app.crud import crud_user
from app.db.database import get_db
from app.db.redis import redis_client
from app.services import jwt_service
from app.services.auth_service import AuthService, auth_service

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/register", status_code=status.HTTP_201_CREATED, response_model=Response[schemas.UserWithToken])
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    logger.info(f"Registering user with email: {user.email}")
    db_user = crud_user.get_user_by_email(db, email=str(user.email))
    if db_user:
        logger.warning(f"Email {db_user.email} already registered.")
        raise BusinessException(ResultCode.EMAIL_ALREADY_REGISTERED)

    new_db_user = crud_user.create_user(db=db, user=user)
    logger.info(f"User {new_db_user.email} registered successfully.")

    access_token = jwt_service.create_access_token(data={"sub": new_db_user.email})
    refresh_token = jwt_service.create_refresh_token(data={"sub": new_db_user.email})

    return Response(
        data=schemas.UserWithToken(
            user=schemas.UserPublic.model_validate(new_db_user),
            token=schemas.Token(access_token=access_token, refresh_token=refresh_token, token_type="bearer")
        )
    )


@router.post("/login", response_model=Response[schemas.UserWithToken])
def login(
        user_credentials: schemas.UserLogin,
        db: Session = Depends(get_db),
        service: AuthService = Depends(lambda: auth_service)
):
    """
    Handles user login by delegating all logic to the AuthService.
    """
    logger.info(f"Login attempt for user: {user_credentials.email}")
    login_data = service.login_user(db, user_credentials)
    logger.info(f"User {login_data.user.email} logged in successfully.")

    return Response(data=login_data)


@router.post("/refresh", response_model=Response[schemas.Token])
def refresh_token(request: schemas.TokenRefreshRequest, db: Session = Depends(get_db)):
    logger.info("Attempting to refresh token.")
    email = jwt_service.verify_token(request.refresh_token)

    # Check if refresh token is valid (exists in Redis)
    stored_token = redis_client.get(f"refresh_token:{email}")
    if not stored_token or stored_token.decode('utf-8') != request.refresh_token:
        logger.warning(f"Invalid refresh token for email: {email}")
        raise BusinessException(ResultCode.INVALID_REFRESH_TOKEN)

    db_user = crud_user.get_user_by_email(db, email=email)
    if not db_user:
        logger.error(f"User not found for email: {email} during token refresh.")
        raise BusinessException(ResultCode.INVALID_CREDENTIALS)

    access_token = jwt_service.create_access_token(data={"sub": db_user.email})
    new_refresh_token = jwt_service.create_refresh_token(data={"sub": db_user.email})
    logger.info(f"Token refreshed successfully for user: {db_user.email}")

    return Response(data=schemas.Token(access_token=access_token, refresh_token=new_refresh_token, token_type="bearer"))
