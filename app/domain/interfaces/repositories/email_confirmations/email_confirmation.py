from abc import abstractmethod

from domain.exceptions import EmailConfirmationNotFoundError
from domain.interfaces.repositories.base import BaseRepo
from domain.models import EmailConfirmation


class EmailConfirmationRepo(BaseRepo):
    """Email confirmation repository."""

    @abstractmethod
    async def get_next_id(self) -> int:
        """Get next ID."""

    @abstractmethod
    async def create(self, confirmation: EmailConfirmation) -> None:
        """Create an email confirmation."""

    @abstractmethod
    async def get_by_token(self, token: str) -> EmailConfirmation | None:
        """Get by token."""

    async def get_by_token_or_raise(self, token: str) -> EmailConfirmation:
        """Get by token or raise exception"""
        email_confirmation = await self.get_by_token(token)
        if not email_confirmation:
            msg = 'EmailConfirmation not found'
            raise EmailConfirmationNotFoundError(msg)

        return email_confirmation

    @abstractmethod
    async def update(self, confirmation: EmailConfirmation) -> None:
        """Update an email confirmation."""
