from typing import override

from sqlalchemy import select, text

from adapters.databases.sqlalchemy.models import EmailConfirmationORM
from adapters.databases.sqlalchemy.repositories.base import SQLABaseRepo
from domain.exceptions import NotFoundError
from domain.interfaces.repositories import EmailConfirmationRepo
from domain.models import EmailConfirmation


class SQLAEmailConfirmationRepo(SQLABaseRepo, EmailConfirmationRepo):
    """Реализация репозитория подтверждения почты на SQLAlchemy."""

    @override
    async def get_next_id(self) -> int:
        res = await self.session.execute(text("select nextval('email_confirmations_id_seq')"))
        return res.scalar_one()

    @override
    async def create(self, confirmation: EmailConfirmation) -> None:
        confirmation_orm = EmailConfirmationORM(**confirmation.model_dump())
        self.session.add(confirmation_orm)
        await self.session.flush()
        await self.session.refresh(confirmation_orm)

    @override
    async def get_by_token(self, token: str) -> EmailConfirmation | None:
        result = await self.session.execute(select(EmailConfirmationORM).where(EmailConfirmationORM.token == token))
        confirmation_orm = result.scalar_one_or_none()
        if confirmation_orm is None:
            return None
        return confirmation_orm.to_domain()

    @override
    async def update(self, confirmation: EmailConfirmation) -> None:
        confirmation_orm = await self.session.get(EmailConfirmationORM, confirmation.id)
        if confirmation_orm is None:
            msg = f'Email confirmation with id={confirmation.id} not found'
            raise NotFoundError(msg)
        for field, value in confirmation.model_dump().items():
            setattr(confirmation_orm, field, value)
        await self.session.flush()
