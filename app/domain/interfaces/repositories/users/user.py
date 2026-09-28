from abc import abstractmethod
from uuid import UUID

from domain.exceptions import UserNotFoundError
from domain.interfaces.repositories.base import BaseRepo
from domain.models import User


class UserRepo(BaseRepo):
    """User repository"""

    @abstractmethod
    async def get_next_id(self) -> int:
        """Get next ID"""

    @abstractmethod
    async def create(self, user: User) -> None:
        """Create new User"""

    @abstractmethod
    async def get_by_email(self, email: str) -> User | None:
        """Get by email"""

    async def get_by_email_or_raise(self, email: str) -> User:
        """Get by email or raise exception"""
        user = await self.get_by_email(email)
        if not user:
            msg = f'User with email={email} not found'
            raise UserNotFoundError(msg)

        return user

    @abstractmethod
    async def get_by_id(self, user_id: int) -> User | None:
        """Get by id"""

    async def get_by_id_or_raise(self, user_id: int) -> User:
        """Get by id or riase exception"""
        user = await self.get_by_id(user_id)
        if not user:
            msg = f'User with id={user_id} not found'
            raise UserNotFoundError(msg)

        return user

    @abstractmethod
    async def get_by_uuid(self, user_uuid: UUID) -> User | None:
        """Get by uuid"""

    @abstractmethod
    async def get_by_nickname(self, nickname: str) -> User | None:
        """Get by nickname"""

    @abstractmethod
    async def update(self, user: User) -> None:
        """Update user"""
