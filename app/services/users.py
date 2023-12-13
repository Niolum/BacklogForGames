"""Module with user services"""

from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from jose import JWTError, jwt

from app.repositories.users import UserRepository
from app.settings import setting
from app.schemas.users import TokenData


class UserService:
    """Class Service for User"""

    def __init__(self, user_repository: UserRepository) -> None:
        self._repository: UserRepository = user_repository

    async def get_users(self, async_session: AsyncSession,):
        """Get all users"""
        return await self._repository.get_all(async_session)

    async def get_user_by_id(self, async_session: AsyncSession, user_id: str):
        """Get user by id"""
        return await self._repository.get_by_id(async_session, user_id)

    async def create_user(
        self,
        async_session: AsyncSession,
        username: str,
        email: str,
        password: str,
        first_name: str | None,
        last_name: str | None,
        avatar: str | None
    ):
        """Create user"""
        return await self._repository.add(
            async_session=async_session,
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            avatar=avatar
        )

    async def delete_user(self, async_session: AsyncSession, user_id: str):
        """Delete user"""
        return await self._repository.delete_by_id(async_session, user_id)

    async def get_user_by_username(self, async_session: AsyncSession, username: str):
        """Get user by username"""
        return await self._repository.get_by_username(async_session, username)



class CurrentUserService:
    """Class for work with current user"""
    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/token")

    def __init__(self, user_repository: UserRepository) -> None:
        self._repository: UserRepository = user_repository

    async def get_current_user(
            self,
            token: Annotated[str, Depends(oauth2_scheme)],
            async_session: AsyncSession
        ):
        """Getting current user"""
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        try:
            payload = jwt.decode(token, setting.SECRET_KEY, algorithms=[setting.ALGORITHM])
            username: str | None = payload.get("sub")
            if username is None:
                raise credentials_exception
            token_data = TokenData(username=username)
        except JWTError:
            raise credentials_exception
        user = await self._repository.get_by_username(
            async_session=async_session,
            username=token_data.username
        )
        if user is None:
            raise credentials_exception
        return user
