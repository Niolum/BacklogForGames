import pytest

from adapters.databases.in_memory.repositories.users.user import InMemUserRepo
from domain.exceptions import BacklogGamesConflictError
from domain.services.auth.service import AuthService
from domain.services.auth.types import CreateUserData


async def test_register_user_stores_lowercased_email() -> None:
    """The service stores a new user and lowercases the whole email."""
    service = AuthService(InMemUserRepo())

    await service.register_user(CreateUserData(email='User@Mail.RU', password='secret', nickname='nick'))

    stored = await InMemUserRepo().get_by_email('user@mail.ru')
    assert stored is not None
    assert stored.email == 'user@mail.ru'
    assert stored.nickname == 'nick'
    assert stored.password != 'secret'


async def test_register_user_rejects_duplicate_email() -> None:
    """The service rejects a second user with the same email."""
    service = AuthService(InMemUserRepo())
    await service.register_user(CreateUserData(email='a@mail.ru', password='secret', nickname='nick'))

    with pytest.raises(BacklogGamesConflictError, match='User with email=a@mail.ru already exists'):
        await service.register_user(CreateUserData(email='a@mail.ru', password='secret', nickname='other'))
