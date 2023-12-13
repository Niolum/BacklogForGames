"""Module for auth services"""

from datetime import datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession
from passlib.context import CryptContext
from jose import jwt

from app.repositories.users import UserRepository
from app.settings import setting


class AuthService:
    """Class Service for auth"""
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def __init__(self, user_repository: UserRepository) -> None:
        self._repository: UserRepository = user_repository

    def get_password_hash(self, password: str):
        """Create hash for password"""
        return self.pwd_context.hash(password)

    def verify_password(self, password: str, hashed_password: str):
        """Verify hash password"""
        return self.pwd_context.verify(password, hashed_password)

    async def authenticate_user(self, async_session: AsyncSession, username: str, password: str):
        """Function for authenticate user"""
        user = await self._repository.get_by_username(async_session, username)
        if not user:
            return False
        if not self.verify_password(password, user.hashed_password):
            return False
        return user

    def create_access_token(self, data: dict, expires_delta: timedelta | None):
        """Create access token"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, setting.SECRET_KEY, algorithm=setting.ALGORITHM)
        return encoded_jwt
