from pydantic import BaseModel

from .user import UserPublic


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str


class TokenRefreshRequest(BaseModel):
    refresh_token: str


class UserWithToken(BaseModel):
    user: UserPublic
    token: Token
