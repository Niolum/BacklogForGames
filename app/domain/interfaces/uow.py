from abc import ABC, abstractmethod
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from domain.interfaces.repositories import UserRepo


class UnitOfWork(ABC):
    """Abstract class for Unit of Work"""

    users: 'UserRepo'

    @abstractmethod
    async def begin(self) -> None:
        """Начать транзакцию"""

    @abstractmethod
    async def commit(self) -> None:
        """Коммит транзакции."""

    @abstractmethod
    async def rollback(self) -> None:
        """Откат транзакции."""

    async def __aenter__(self):
        await self.begin()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            await self.rollback()
        else:
            await self.commit()
