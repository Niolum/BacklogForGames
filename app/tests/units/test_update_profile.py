from datetime import date

import pytest
from pydantic import ValidationError

from adapters.databases.in_memory.repositories.users.user import InMemUserRepo
from deps.container import DIContainer
from domain.exceptions import BacklogGamesConflictError
from domain.services import UpdateProfileData
from domain.services.auth.types import CreateUserData


def test_update_profile_data_rejects_null_nickname() -> None:
    """An explicit null nickname is invalid. An omitted nickname is allowed."""
    with pytest.raises(ValidationError):
        UpdateProfileData(nickname=None)

    data = UpdateProfileData(about='hello')
    assert 'nickname' not in data.model_dump(exclude_unset=True)


async def test_update_profile_changes_fields(di_container: DIContainer) -> None:
    """The service stores nickname, date of birth and about for the given user."""
    await di_container.auth_service().register_user(
        CreateUserData(email='user@mail.ru', password='secret', nickname='nick'),
    )
    user = await InMemUserRepo().get_by_email('user@mail.ru')
    assert user is not None

    updated = await di_container.user_service().update_profile(
        user,
        UpdateProfileData(nickname='renamed', date_birth=date(1990, 1, 2), about='hello'),
    )

    assert updated.nickname == 'renamed'
    assert updated.date_birth == date(1990, 1, 2)
    assert updated.about == 'hello'
    assert updated.email == 'user@mail.ru'
    stored = await InMemUserRepo().get_by_email('user@mail.ru')
    assert stored == updated


async def test_update_profile_keeps_another_user(di_container: DIContainer) -> None:
    """Changing one profile leaves the other user untouched."""
    auth = di_container.auth_service()
    await auth.register_user(CreateUserData(email='user@mail.ru', password='secret', nickname='nick'))
    await auth.register_user(CreateUserData(email='other@mail.ru', password='secret', nickname='other'))
    user = await InMemUserRepo().get_by_email('user@mail.ru')
    assert user is not None

    await di_container.user_service().update_profile(user, UpdateProfileData(nickname='renamed', about='hello'))

    other = await InMemUserRepo().get_by_email('other@mail.ru')
    assert other is not None
    assert other.nickname == 'other'
    assert other.about is None


async def test_update_profile_rejects_taken_nickname(di_container: DIContainer) -> None:
    """A nickname owned by another user raises a conflict."""
    auth = di_container.auth_service()
    await auth.register_user(CreateUserData(email='user@mail.ru', password='secret', nickname='nick'))
    await auth.register_user(CreateUserData(email='other@mail.ru', password='secret', nickname='other'))
    user = await InMemUserRepo().get_by_email('user@mail.ru')
    assert user is not None

    with pytest.raises(BacklogGamesConflictError, match='User with nickname=other already exists'):
        await di_container.user_service().update_profile(user, UpdateProfileData(nickname='other'))

    stored = await InMemUserRepo().get_by_email('user@mail.ru')
    assert stored is not None
    assert stored.nickname == 'nick'
