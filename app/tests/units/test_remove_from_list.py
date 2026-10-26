from uuid import UUID

import pytest

from adapters.databases.in_memory.repositories.users.user import InMemUserRepo
from deps.container import DIContainer
from domain.exceptions import GameNotFoundError, UserGameNotFoundError
from domain.models import User
from domain.services import AddUserGameData
from domain.services.auth.types import CreateUserData
from domain.use_cases import add_to_backlog, get_user_backlog, get_user_completed, remove_from_list
from tests.fixtures.game import Catalog


async def test_remove_from_list_deletes_a_backlog_row(listed_user: User, catalog: Catalog) -> None:
    """The caller's backlog row is removed and the completed row stays."""
    await remove_from_list(listed_user, catalog.planescape.uuid)
    backlog = await get_user_backlog(listed_user.uuid, limit=20, offset=0)
    completed = await get_user_completed(listed_user.uuid, limit=20, offset=0)

    assert [item.title for item in backlog.items] == [catalog.disco.title]
    assert backlog.total == 1
    assert [item.game.title for item in completed.items] == [catalog.torment.title]


async def test_remove_from_list_deletes_a_completed_row(listed_user: User, catalog: Catalog) -> None:
    """The caller's completed row is removed and the backlog stays."""
    await remove_from_list(listed_user, catalog.torment.uuid)
    backlog = await get_user_backlog(listed_user.uuid, limit=20, offset=0)
    completed = await get_user_completed(listed_user.uuid, limit=20, offset=0)

    assert [item.title for item in backlog.items] == [catalog.disco.title, catalog.planescape.title]
    assert completed.items == []
    assert completed.total == 0


async def test_remove_from_list_rejects_a_missing_row(registered_user: User, catalog: Catalog) -> None:
    """A game that is not in the caller's lists stays absent."""
    with pytest.raises(UserGameNotFoundError, match=f'Game with uuid={catalog.planescape.uuid} is not listed'):
        await remove_from_list(registered_user, catalog.planescape.uuid)

    backlog = await get_user_backlog(registered_user.uuid, limit=20, offset=0)
    completed = await get_user_completed(registered_user.uuid, limit=20, offset=0)
    assert backlog.total == 0
    assert completed.total == 0


async def test_remove_from_list_rejects_an_unknown_game(registered_user: User) -> None:
    """An unknown game is not stored."""
    missing_game_uuid = UUID('00000000-0000-0000-0000-000000000099')

    with pytest.raises(GameNotFoundError, match=f'Game with uuid={missing_game_uuid} not found'):
        await remove_from_list(registered_user, missing_game_uuid)

    backlog = await get_user_backlog(registered_user.uuid, limit=20, offset=0)
    assert backlog.total == 0


async def test_remove_from_list_leaves_another_users_row(
    di_container: DIContainer,
    registered_user: User,
    catalog: Catalog,
) -> None:
    """Another user cannot remove a row that belongs to someone else."""
    await add_to_backlog(registered_user, AddUserGameData(game_uuid=catalog.planescape.uuid))
    await di_container.auth_service().register_user(
        CreateUserData(email='other@mail.ru', password='secret', nickname='other'),
    )
    other = await InMemUserRepo().get_by_email('other@mail.ru')
    assert other is not None

    with pytest.raises(UserGameNotFoundError, match=f'Game with uuid={catalog.planescape.uuid} is not listed'):
        await remove_from_list(other, catalog.planescape.uuid)

    page = await get_user_backlog(registered_user.uuid, limit=20, offset=0)
    assert [item.title for item in page.items] == [catalog.planescape.title]
    assert page.total == 1
