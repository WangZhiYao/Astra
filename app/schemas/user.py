from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, ConfigDict


class UserBase(BaseModel):
    email: EmailStr


class UserCreate(UserBase):
    password: str


class UserLogin(UserBase):
    password: str


class UserPublic(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nickname: str
    last_login_at: Optional[datetime] = None
    created_at: datetime


class User(UserPublic):
    model_config = ConfigDict(from_attributes=True)

    password_hash: str
    is_active: bool
    is_admin: bool
    updated_at: datetime
