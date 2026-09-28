from uuid import uuid4

import pytest

from adapters.databases.in_memory.repositories.users.user import InMemUserRepo
from domain.exceptions import UserNotFoundError


async def test_get_by_uuid_or_raise_returns_user(access_token: str) -> None:
    """The repository returns the user stored under the public uuid."""
    assert access_token
    stored = await InMemUserRepo().get_by_email('user@mail.ru')
    assert stored is not None

    loaded = await InMemUserRepo().get_by_uuid_or_raise(stored.uuid)

    assert loaded == stored


async def test_get_by_uuid_or_raise_missing_user() -> None:
    """An unknown uuid raises not found."""
    missing = uuid4()

    with pytest.raises(UserNotFoundError, match=f'User with uuid={missing} not found'):
        await InMemUserRepo().get_by_uuid_or_raise(missing)
