from typing import ClassVar, override

from adapters.databases.in_memory.repositories.base import InMemBaseRepo
from domain.exceptions import NotFoundError
from domain.interfaces.repositories import EmailConfirmationRepo
from domain.models import EmailConfirmation


class InMemEmailConfirmationRepo(InMemBaseRepo[EmailConfirmation], EmailConfirmationRepo):
    """In-memory email confirmation repository."""

    DB: ClassVar[dict[int, EmailConfirmation]] = {}

    @override
    async def create(self, confirmation: EmailConfirmation) -> None:
        self._store(confirmation)

    @override
    async def get_by_token(self, token: str) -> EmailConfirmation | None:
        return self._get(token=token)

    @override
    async def update(self, confirmation: EmailConfirmation) -> None:
        if self._get(id=confirmation.id) is None:
            msg = f'Email confirmation with id={confirmation.id} not found'
            raise NotFoundError(msg)
        self._update(confirmation)
