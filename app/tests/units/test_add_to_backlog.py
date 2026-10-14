from uuid import UUID

import pytest

from adapters.databases.in_memory.repositories.users.user import InMemUserRepo
from deps.container import DIContainer
from domain.exceptions import GameNotFoundError, UserGameAlreadyListedError
from domain.models import User, UserGameStatus
from domain.services import AddUserGameData
from domain.services.auth.types import CreateUserData
from domain.use_cases import add_to_backlog, get_user_backlog, get_user_completed
from tests.fixtures.game import Catalog


async def test_add_to_backlog_stores_a_backlog_row(registered_user: User, catalog: Catalog) -> None:
    """A game missing from both lists is stored as backlog without a completion time."""
    entry = await add_to_backlog(registered_user, AddUserGameData(game_uuid=catalog.planescape.uuid))
    page = await get_user_backlog(registered_user.uuid, limit=20, offset=0)

    assert entry.user_id == registered_user.id
    assert entry.game_id == catalog.planescape.id
    assert entry.status is UserGameStatus.backlog
    assert entry.completed_at is None
    assert [item.title for item in page.items] == [catalog.planescape.title]
    assert page.items[0].cover_url == catalog.planescape.cover_url
    assert page.total == 1


async def test_add_to_backlog_rejects_an_unknown_game(registered_user: User) -> None:
    """An unknown game is not stored."""
    missing_game_uuid = UUID('00000000-0000-0000-0000-000000000099')

    with pytest.raises(GameNotFoundError, match=f'Game with uuid={missing_game_uuid} not found'):
        await add_to_backlog(registered_user, AddUserGameData(game_uuid=missing_game_uuid))

    page = await get_user_backlog(registered_user.uuid, limit=20, offset=0)
    assert page.items == []
    assert page.total == 0


async def test_add_to_backlog_rejects_a_game_already_in_the_backlog(listed_user: User, catalog: Catalog) -> None:
    """A second backlog request leaves the existing row in place."""
    backlog_titles = [catalog.disco.title, catalog.planescape.title]

    with pytest.raises(
        UserGameAlreadyListedError,
        match=f'Game with uuid={catalog.planescape.uuid} is already listed',
    ):
        await add_to_backlog(listed_user, AddUserGameData(game_uuid=catalog.planescape.uuid))

    page = await get_user_backlog(listed_user.uuid, limit=20, offset=0)
    assert [item.title for item in page.items] == backlog_titles
    assert page.total == len(backlog_titles)


async def test_add_to_backlog_rejects_a_completed_game(listed_user: User, catalog: Catalog) -> None:
    """A completed game stays completed and is not copied into the backlog."""
    with pytest.raises(
        UserGameAlreadyListedError,
        match=f'Game with uuid={catalog.torment.uuid} is already listed',
    ):
        await add_to_backlog(listed_user, AddUserGameData(game_uuid=catalog.torment.uuid))

    backlog = await get_user_backlog(listed_user.uuid, limit=20, offset=0)
    completed = await get_user_completed(listed_user.uuid, limit=20, offset=0)
    assert catalog.torment.title not in [item.title for item in backlog.items]
    assert [item.title for item in completed.items] == [catalog.torment.title]


async def test_add_to_backlog_allows_the_same_game_for_another_user(
    di_container: DIContainer,
    registered_user: User,
    catalog: Catalog,
) -> None:
    """Each user has a separate backlog entry for the same game."""
    await add_to_backlog(registered_user, AddUserGameData(game_uuid=catalog.planescape.uuid))
    await di_container.auth_service().register_user(
        CreateUserData(email='other@mail.ru', password='secret', nickname='other'),
    )
    other = await InMemUserRepo().get_by_email('other@mail.ru')
    assert other is not None

    entry = await add_to_backlog(other, AddUserGameData(game_uuid=catalog.planescape.uuid))
    page = await get_user_backlog(other.uuid, limit=20, offset=0)

    assert entry.user_id == other.id
    assert entry.status is UserGameStatus.backlog
    assert [item.title for item in page.items] == [catalog.planescape.title]
