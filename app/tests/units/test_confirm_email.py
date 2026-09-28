from datetime import datetime, timedelta

import pytest

from adapters.databases.in_memory.repositories.email_confirmations.email_confirmation import InMemEmailConfirmationRepo
from adapters.databases.in_memory.repositories.users.user import InMemUserRepo
from config import settings
from dependencies.container import DIContainer
from domain.exceptions import BadRequestError, NotFoundError
from domain.models import EmailConfirmation


async def test_confirm_email_marks_user_and_consumes_token(
    di_container: DIContainer,
    confirmation_token: str,
) -> None:
    """A valid token confirms the email and records the time it was used."""
    await di_container.auth_service().confirm_email(confirmation_token)

    stored = await InMemUserRepo().get_by_email('user@mail.ru')
    confirmation = await InMemEmailConfirmationRepo().get_by_token(confirmation_token)
    assert stored is not None
    assert stored.email_confirmed is True
    assert confirmation is not None
    assert confirmation.used_at is not None


async def test_confirm_email_rejects_used_token(di_container: DIContainer, confirmation_token: str) -> None:
    """A token that was already used does not confirm the email again."""
    await di_container.auth_service().confirm_email(confirmation_token)
    used_at = (await InMemEmailConfirmationRepo().get_by_token_or_raise(confirmation_token)).used_at

    with pytest.raises(BadRequestError, match='Confirmation token is invalid'):
        await di_container.auth_service().confirm_email(confirmation_token)

    confirmation = await InMemEmailConfirmationRepo().get_by_token(confirmation_token)
    assert confirmation is not None
    assert confirmation.used_at == used_at


async def test_confirm_email_rejects_expired_token(di_container: DIContainer, confirmation_token: str) -> None:
    """An expired token leaves the email unconfirmed."""
    confirmation = await InMemEmailConfirmationRepo().get_by_token(confirmation_token)
    assert confirmation is not None
    expired_at = datetime.now(settings.default_timezone) - timedelta(hours=1)
    await InMemEmailConfirmationRepo().update(confirmation.model_copy(update={'expires_at': expired_at}))

    with pytest.raises(BadRequestError, match='Confirmation token is invalid'):
        await di_container.auth_service().confirm_email(confirmation_token)

    stored = await InMemUserRepo().get_by_email('user@mail.ru')
    confirmation = await InMemEmailConfirmationRepo().get_by_token(confirmation_token)
    assert stored is not None
    assert stored.email_confirmed is False
    assert confirmation is not None
    assert confirmation.used_at is None


async def test_confirm_email_rejects_unknown_token(di_container: DIContainer, confirmation_token: str) -> None:
    """An unknown token does not confirm any email."""
    with pytest.raises(BadRequestError, match='Confirmation token is invalid'):
        await di_container.auth_service().confirm_email('missing')

    stored = await InMemUserRepo().get_by_email('user@mail.ru')
    confirmation = await InMemEmailConfirmationRepo().get_by_token(confirmation_token)
    assert stored is not None
    assert stored.email_confirmed is False
    assert confirmation is not None
    assert confirmation.used_at is None


async def test_confirm_email_missing_user_raises(di_container: DIContainer) -> None:
    """A token that points to a missing user raises not found."""
    expires_at = datetime.now(settings.default_timezone) + timedelta(hours=1)
    await InMemEmailConfirmationRepo().create(
        EmailConfirmation(id=1, user_id=99, token='orphan', expires_at=expires_at),
    )

    with pytest.raises(NotFoundError, match='User with id=99 not found'):
        await di_container.auth_service().confirm_email('orphan')
