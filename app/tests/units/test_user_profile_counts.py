from uuid import uuid4

import pytest

from domain.exceptions import UserNotFoundError
from domain.models import User
from domain.services import AddUserGameData
from domain.use_cases import add_to_backlog, add_to_completed, get_user_profile
from tests.fixtures.game import Catalog


async def test_get_user_profile_counts_empty_lists(registered_user: User) -> None:
    """A user without list rows has zero counts."""
    profile = await get_user_profile(registered_user.uuid)

    assert profile.user.uuid == registered_user.uuid
    assert profile.counts.backlog_count == 0
    assert profile.counts.completed_count == 0


async def test_get_user_profile_counts_only_that_users_rows(listed_user: User, catalog: Catalog) -> None:
    """Backlog and completed rows are counted separately, and another user's row is not."""
    profile = await get_user_profile(listed_user.uuid)
    backlog_games = [catalog.planescape, catalog.disco]
    completed_games = [catalog.torment]

    assert profile.counts.backlog_count == len(backlog_games)
    assert profile.counts.completed_count == len(completed_games)


async def test_get_user_profile_skips_a_hidden_game(registered_user: User, catalog: Catalog) -> None:
    """A hidden game stays on the list and is left out of the counts."""
    await add_to_backlog(registered_user, AddUserGameData(game_uuid=catalog.hidden.uuid))
    await add_to_completed(registered_user, AddUserGameData(game_uuid=catalog.disco.uuid))

    profile = await get_user_profile(registered_user.uuid)
    published = [catalog.disco]

    assert profile.counts.backlog_count == 0
    assert profile.counts.completed_count == len(published)


async def test_get_user_profile_rejects_an_unknown_user() -> None:
    """An unknown user is not counted."""
    missing = uuid4()

    with pytest.raises(UserNotFoundError, match=f'User with uuid={missing} not found'):
        await get_user_profile(missing)
