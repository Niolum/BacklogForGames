import pytest

from adapters.databases.in_memory.repositories.email_confirmations.email_confirmation import InMemEmailConfirmationRepo
from adapters.databases.in_memory.repositories.users.user import InMemUserRepo
from dependencies.container import DIContainer
from domain.exceptions import BadRequestError, UserNotFoundError


async def test_resend_confirmation_creates_another_unused_token(
    di_container: DIContainer,
    confirmation_token: str,
) -> None:
    """Resend stores a second unused token and leaves the email unconfirmed."""
    await di_container.auth_service().resend_confirmation_email('user@mail.ru')

    stored = await InMemUserRepo().get_by_email('user@mail.ru')
    confirmations = list(InMemEmailConfirmationRepo.DB.values())
    extra = [item for item in confirmations if item.token != confirmation_token]
    assert stored is not None
    assert stored.email_confirmed is False
    assert len(extra) == 1
    assert extra[0].used_at is None
    assert extra[0].user_id == stored.id
    assert all(item.used_at is None for item in confirmations)


async def test_resend_confirmation_rejects_confirmed_email(
    di_container: DIContainer,
    confirmation_token: str,
) -> None:
    """A confirmed email does not receive another confirmation token."""
    await di_container.auth_service().confirm_email(confirmation_token)

    with pytest.raises(BadRequestError, match='Email user@mail.ru is already confirmed'):
        await di_container.auth_service().resend_confirmation_email('user@mail.ru')

    assert len(InMemEmailConfirmationRepo.DB) == 1


async def test_resend_confirmation_rejects_unknown_email(di_container: DIContainer) -> None:
    """An unknown email does not create a confirmation token."""
    with pytest.raises(UserNotFoundError, match='User with email=missing@mail.ru not found'):
        await di_container.auth_service().resend_confirmation_email('missing@mail.ru')

    assert InMemEmailConfirmationRepo.DB == {}
