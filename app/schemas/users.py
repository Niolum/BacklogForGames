"""Module with User scheme"""

from pydantic import BaseModel, UUID4


class UserBase(BaseModel):
    """Base user scheme"""
    username: str
    first_name: str | None
    last_name: str | None
    email: str
    avatar: str | None
    about: str | None


class UserCreate(UserBase):
    """User create scheme"""
    password: str


class User(BaseModel):
    """User scheme"""
    id: UUID4
    username: str
    avatar: str | None


class UserDetail(UserBase):
    """User detail scheme"""
    id: UUID4


class UserUpdate(UserBase):
    """User update scheme"""
    pass


class UserDelete(BaseModel):
    """User delete scheme"""
    message: str


class Token(BaseModel):
    """Token scheme"""
    access_token: str
    token_type: str


class TokenData(BaseModel):
    """TokenData scheme"""
    username: str
