"""Module with User scheme"""

from pydantic import BaseModel, UUID4


class UserBase(BaseModel):
    """Base user scheme"""
    username: str
    first_name: str | None
    last_name: str | None
    email: str
    avatar: str | None


class UserCreate(UserBase):
    """User create scheme"""
    password: str


class User(UserBase):
    """User scheme"""
    id: UUID4


class Token(BaseModel):
    """Token scheme"""
    access_token: str
    token_type: str


class TokenData(BaseModel):
    """TokenData scheme"""
    username: str
