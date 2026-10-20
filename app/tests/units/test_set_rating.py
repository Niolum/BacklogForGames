from uuid import UUID

import pytest

from adapters.databases.in_memory.repositories.ratings.rating import InMemRatingRepo
from adapters.databases.in_memory.repositories.users.user import InMemUserRepo
from deps.container import DIContainer
from domain.exceptions import GameNotCompletedError, GameNotFoundError
from domain.models import User
from domain.services import AddUserGameData, SetRatingData
from domain.services.auth.types import CreateUserData
from domain.use_cases import add_to_backlog, add_to_completed, set_rating
from tests.fixtures.game import Catalog


async def test_set_rating_creates_a_score_for_a_completed_game(registered_user: User, catalog: Catalog) -> None:
    """A completed game without a score stores one row for this user."""
    data = SetRatingData(score=8)
    await add_to_completed(registered_user, AddUserGameData(game_uuid=catalog.disco.uuid))

    rating = await set_rating(registered_user, catalog.disco.uuid, data)
    stored = await InMemRatingRepo().get_by_user_and_game(registered_user.id, catalog.disco.id)

    assert stored is not None
    assert rating.id == stored.id
    assert rating.user_id == registered_user.id
    assert rating.game_id == catalog.disco.id
    assert rating.score == data.score
    assert stored.score == data.score


async def test_set_rating_rejects_an_unknown_game(registered_user: User) -> None:
    """An unknown game is not stored."""
    missing_game_uuid = UUID('00000000-0000-0000-0000-000000000099')

    with pytest.raises(GameNotFoundError, match=f'Game with uuid={missing_game_uuid} not found'):
        await set_rating(registered_user, missing_game_uuid, SetRatingData(score=8))

    assert InMemRatingRepo.DB == {}


async def test_set_rating_rejects_a_game_that_is_not_completed(registered_user: User, catalog: Catalog) -> None:
    """A backlog game and a game absent from the lists do not get a score."""
    await add_to_backlog(registered_user, AddUserGameData(game_uuid=catalog.planescape.uuid))

    with pytest.raises(GameNotCompletedError, match=f'Game with uuid={catalog.planescape.uuid} is not completed'):
        await set_rating(registered_user, catalog.planescape.uuid, SetRatingData(score=8))
    with pytest.raises(GameNotCompletedError, match=f'Game with uuid={catalog.disco.uuid} is not completed'):
        await set_rating(registered_user, catalog.disco.uuid, SetRatingData(score=8))

    summary = await InMemRatingRepo().get_summary(catalog.planescape.id)
    assert summary.ratings_count == 0
    assert await InMemRatingRepo().get_by_user_and_game(registered_user.id, catalog.disco.id) is None


async def test_set_rating_updates_an_existing_score(registered_user: User, catalog: Catalog) -> None:
    """A second score replaces the value and the update time in the same row."""
    first = SetRatingData(score=6)
    second = SetRatingData(score=9)
    await add_to_completed(registered_user, AddUserGameData(game_uuid=catalog.planescape.uuid))
    created = await set_rating(registered_user, catalog.planescape.uuid, first)

    updated = await set_rating(registered_user, catalog.planescape.uuid, second)
    summary = await InMemRatingRepo().get_summary(catalog.planescape.id)

    assert updated.id == created.id
    assert updated.created_at == created.created_at
    assert updated.score == second.score
    assert updated.updated_at >= created.updated_at
    assert summary.ratings_count == 1
    assert summary.users_score == float(second.score)


async def test_set_rating_keeps_another_users_score(
    di_container: DIContainer,
    registered_user: User,
    catalog: Catalog,
) -> None:
    """Each user has a separate score for the same completed game."""
    owner_score = SetRatingData(score=7)
    other_score = SetRatingData(score=10)
    await add_to_completed(registered_user, AddUserGameData(game_uuid=catalog.planescape.uuid))
    await set_rating(registered_user, catalog.planescape.uuid, owner_score)
    await di_container.auth_service().register_user(
        CreateUserData(email='other@mail.ru', password='secret', nickname='other'),
    )
    other = await InMemUserRepo().get_by_email('other@mail.ru')
    assert other is not None
    await add_to_completed(other, AddUserGameData(game_uuid=catalog.planescape.uuid))

    other_rating = await set_rating(other, catalog.planescape.uuid, other_score)
    owner_rating = await InMemRatingRepo().get_by_user_and_game(registered_user.id, catalog.planescape.id)

    assert owner_rating is not None
    assert owner_rating.score == owner_score.score
    assert other_rating.user_id == other.id
    assert other_rating.score == other_score.score
    assert other_rating.id != owner_rating.id
