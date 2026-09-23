from abc import abstractmethod

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
