from uuid import UUID

import pytest

from adapters.databases.in_memory.repositories.users.user import InMemUserRepo
from deps.container import DIContainer
from domain.exceptions import GameNotFoundError, UserGameAlreadyListedError
from domain.models import User, UserGameStatus
from domain.services import AddUserGameData
from domain.services.auth.types import CreateUserData
from domain.use_cases import add_to_backlog, add_to_completed, get_user_backlog, get_user_completed
from tests.fixtures.game import Catalog


async def test_add_to_completed_creates_a_completed_row(registered_user: User, catalog: Catalog) -> None:
    """A game missing from both lists is stored as completed."""
    entry = await add_to_completed(registered_user, AddUserGameData(game_uuid=catalog.disco.uuid))
    backlog = await get_user_backlog(registered_user.uuid, limit=20, offset=0)
    completed = await get_user_completed(registered_user.uuid, limit=20, offset=0)

    assert entry.status is UserGameStatus.completed
    assert entry.completed_at is not None
    assert entry.game_id == catalog.disco.id
    assert backlog.items == []
    assert [item.game.title for item in completed.items] == [catalog.disco.title]
    assert completed.total == 1


async def test_add_to_completed_moves_the_backlog_row(registered_user: User, catalog: Catalog) -> None:
    """A backlog row becomes completed in place and leaves the backlog."""
    backlog_entry = await add_to_backlog(registered_user, AddUserGameData(game_uuid=catalog.planescape.uuid))

    entry = await add_to_completed(registered_user, AddUserGameData(game_uuid=catalog.planescape.uuid))
    backlog = await get_user_backlog(registered_user.uuid, limit=20, offset=0)
    completed = await get_user_completed(registered_user.uuid, limit=20, offset=0)

    assert entry.id == backlog_entry.id
    assert entry.created_at == backlog_entry.created_at
    assert entry.user_id == registered_user.id
    assert entry.game_id == catalog.planescape.id
    assert entry.status is UserGameStatus.completed
    assert entry.completed_at is not None
    assert backlog.items == []
    assert [item.game.title for item in completed.items] == [catalog.planescape.title]


async def test_add_to_completed_rejects_an_already_completed_game(listed_user: User, catalog: Catalog) -> None:
    """A second completion leaves the completed row in place."""
    with pytest.raises(
        UserGameAlreadyListedError,
        match=f'Game with uuid={catalog.torment.uuid} is already completed',
    ):
        await add_to_completed(listed_user, AddUserGameData(game_uuid=catalog.torment.uuid))

    backlog = await get_user_backlog(listed_user.uuid, limit=20, offset=0)
    completed = await get_user_completed(listed_user.uuid, limit=20, offset=0)
    backlog_titles = [catalog.disco.title, catalog.planescape.title]
    assert [item.title for item in backlog.items] == backlog_titles
    assert [item.game.title for item in completed.items] == [catalog.torment.title]


async def test_add_to_completed_rejects_an_unknown_game(registered_user: User) -> None:
    """An unknown game is not stored."""
    missing_game_uuid = UUID('00000000-0000-0000-0000-000000000099')

    with pytest.raises(GameNotFoundError, match=f'Game with uuid={missing_game_uuid} not found'):
        await add_to_completed(registered_user, AddUserGameData(game_uuid=missing_game_uuid))

    completed = await get_user_completed(registered_user.uuid, limit=20, offset=0)
    assert completed.items == []
    assert completed.total == 0


async def test_add_to_completed_allows_the_same_game_for_another_user(
    di_container: DIContainer,
    registered_user: User,
    catalog: Catalog,
) -> None:
    """Each user has a separate completed entry for the same game."""
    await add_to_completed(registered_user, AddUserGameData(game_uuid=catalog.planescape.uuid))
    await di_container.auth_service().register_user(
        CreateUserData(email='other@mail.ru', password='secret', nickname='other'),
    )
    other = await InMemUserRepo().get_by_email('other@mail.ru')
    assert other is not None

    entry = await add_to_completed(other, AddUserGameData(game_uuid=catalog.planescape.uuid))
    page = await get_user_completed(other.uuid, limit=20, offset=0)

    assert entry.user_id == other.id
    assert entry.status is UserGameStatus.completed
    assert [item.game.title for item in page.items] == [catalog.planescape.title]
