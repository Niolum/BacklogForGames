from datetime import datetime

import pytest

from adapters.databases.in_memory.repositories.email_confirmations.email_confirmation import InMemEmailConfirmationRepo
from adapters.databases.in_memory.repositories.users.user import InMemUserRepo
from config import settings
from dependencies.container import DIContainer
from domain.constants import EMAIL_CONFIRMATION_TTL
from domain.exceptions import BacklogGamesConflictError
from domain.services.auth.types import CreateUserData


async def test_register_user_stores_lowercased_email(di_container: DIContainer) -> None:
    """The service stores a new user and lowercases the whole email."""
    service = di_container.auth_service()

    await service.register_user(CreateUserData(email='User@Mail.RU', password='secret', nickname='nick'))

    stored = await InMemUserRepo().get_by_email('user@mail.ru')
    assert stored is not None
    assert stored.email == 'user@mail.ru'
    assert stored.nickname == 'nick'
    assert stored.password != 'secret'
    assert stored.avatar_url is None
    assert stored.email_confirmed is False
    assert stored.is_admin is False


async def test_register_user_creates_unused_confirmation(di_container: DIContainer) -> None:
    """Registration stores an unused token and leaves the email unconfirmed."""
    service = di_container.auth_service()

    await service.register_user(CreateUserData(email='User@Mail.RU', password='secret', nickname='nick'))

    stored = await InMemUserRepo().get_by_email('user@mail.ru')
    assert stored is not None
    assert stored.email_confirmed is False
    confirmations = list(InMemEmailConfirmationRepo.DB.values())
    assert len(confirmations) == 1
    confirmation = confirmations[0]
    assert confirmation.user_id == stored.id
    assert confirmation.used_at is None
    now = datetime.now(settings.default_timezone)
    assert now < confirmation.expires_at <= now + EMAIL_CONFIRMATION_TTL


async def test_register_user_rejects_duplicate_email(di_container: DIContainer) -> None:
    """The service rejects a second user with the same email."""
    service = di_container.auth_service()
    await service.register_user(CreateUserData(email='a@mail.ru', password='secret', nickname='nick'))

    with pytest.raises(BacklogGamesConflictError, match='User with email=a@mail.ru already exists'):
        await service.register_user(CreateUserData(email='a@mail.ru', password='secret', nickname='other'))

    assert len(InMemEmailConfirmationRepo.DB) == 1
