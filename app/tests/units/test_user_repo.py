from pathlib import Path
from uuid import uuid4

import pytest

from adapters.databases.in_memory.repositories.users.user import InMemUserRepo
from domain.exceptions import NotFoundError
from domain.models import User


def _user(**overrides) -> User:
    data = {
        'id': 1,
        'uuid': uuid4(),
        'nickname': 'nick',
        'email': 'user@mail.ru',
        'password': 'hash',
        'avatar_url': Path('avatars/user.png'),
    }
    return User.model_validate(data | overrides, from_attributes=True)


async def test_user_repo_finds_user_by_id_uuid_and_nickname() -> None:
    """The repository returns the same user by id, uuid and nickname."""
    repo = InMemUserRepo()
    user = _user()
    await repo.create(user)

    assert await repo.get_by_id(user.id) == user
    assert await repo.get_by_uuid(user.uuid) == user
    assert await repo.get_by_nickname(user.nickname) == user
    assert await repo.get_by_id(99) is None
    assert await repo.get_by_uuid(uuid4()) is None
    assert await repo.get_by_nickname('missing') is None


async def test_user_repo_updates_existing_user() -> None:
    """Update replaces the stored user and keeps the same id."""
    repo = InMemUserRepo()
    user = _user()
    await repo.create(user)
    changed = user.model_copy(update={'nickname': 'new-nick', 'about': 'hello', 'avatar_url': None})

    await repo.update(changed)

    stored = await repo.get_by_id(user.id)
    assert stored is not None
    assert stored.nickname == 'new-nick'
    assert stored.about == 'hello'
    assert stored.avatar_url is None
    assert await repo.get_by_nickname('nick') is None
    assert await repo.get_by_nickname('new-nick') == stored


async def test_user_repo_update_missing_user_raises() -> None:
    """Update of an unknown id raises not found."""
    repo = InMemUserRepo()

    with pytest.raises(NotFoundError, match='User with id=1 not found'):
        await repo.update(_user())
