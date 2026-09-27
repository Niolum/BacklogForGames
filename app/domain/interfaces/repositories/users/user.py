from abc import abstractmethod
from uuid import UUID

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

    @abstractmethod
    async def get_by_id(self, user_id: int) -> User | None:
        """Get by id"""

    @abstractmethod
    async def get_by_uuid(self, user_uuid: UUID) -> User | None:
        """Get by uuid"""

    @abstractmethod
    async def get_by_nickname(self, nickname: str) -> User | None:
        """Get by nickname"""

    @abstractmethod
    async def update(self, user: User) -> None:
        """Update user"""
