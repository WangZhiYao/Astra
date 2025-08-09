# app/services/auth_service.py

from sqlalchemy.orm import Session

import app.crud.crud_user as crud_user
from app import schemas
from app.core.config import settings
from app.core.exceptions import BusinessException, ResultCode
from app.core.security import verify_password
from app.db.redis import redis_client
from app.services import jwt_service


class AuthService:

    def _handle_failed_login_attempt(self, email: str):
        """Manages rate limiting for failed login attempts using Redis."""
        login_attempts_key = f"failed_login_attempts:{email}"
        attempts = redis_client.incr(login_attempts_key)

        # Set expiry on the first failed attempt
        if attempts == 1:
            redis_client.expire(login_attempts_key, settings.LOGIN_ATTEMPT_WINDOW_MINUTES * 60)

        if attempts >= settings.MAX_LOGIN_ATTEMPTS:
            # Log this attempt before raising an exception
            raise BusinessException(ResultCode.TOO_MANY_LOGIN_ATTEMPTS)

    def login_user(self, db: Session, user_credentials: schemas.UserLogin) -> schemas.UserWithToken:
        """
        Orchestrates the entire user login process.
        Returns the user model and a token schema.
        """
        email = str(user_credentials.email)
        password = user_credentials.password

        # 1. Check rate limiting first
        login_attempts_key = f"failed_login_attempts:{email}"
        if redis_client.get(login_attempts_key) and int(
                redis_client.get(login_attempts_key)) >= settings.MAX_LOGIN_ATTEMPTS:
            raise BusinessException(ResultCode.TOO_MANY_LOGIN_ATTEMPTS)

        # 2. Fetch user from DB using the refactored CRUD function
        db_user = crud_user.get_user_by_email(db, email=email)

        # 3. Validate user and password
        if not db_user or not verify_password(password, db_user.password_hash):
            self._handle_failed_login_attempt(email)
            raise BusinessException(ResultCode.LOGIN_FAILED)

        if not db_user.is_active:
            raise BusinessException(ResultCode.INACTIVE_USER)

        # 4. On success, update login time using the already-fetched user object
        crud_user.update_user_login_timestamp(db, db_user=db_user)

        # 5. Commit the session to save the last_login_at update
        db.commit()
        db.refresh(db_user)

        # 6. Clear any failed login attempts from Redis
        redis_client.delete(login_attempts_key)

        # 7. Create tokens
        access_token = jwt_service.create_access_token(data={"sub": db_user.email})
        refresh_token = jwt_service.create_refresh_token(data={"sub": db_user.email})

        token = schemas.Token(access_token=access_token, refresh_token=refresh_token, token_type="bearer")

        return schemas.UserWithToken(
            user=schemas.UserPublic.model_validate(db_user),
            token=token
        )


# Create a singleton instance to be used with Depends
auth_service = AuthService()
