import pytest

from adapters.databases.in_memory.repositories.users.user import InMemUserRepo
from deps.container import DIContainer
from domain.exceptions import GameNotFoundError
from domain.models import User, UserGameStatus
from domain.services import AddUserGameData, SetRatingData
from domain.services.auth.types import CreateUserData
from domain.use_cases import add_to_backlog, add_to_completed, get_game_card, set_rating
from tests.fixtures.game import Catalog


async def test_get_game_card_has_no_scores_yet(catalog: Catalog) -> None:
    """A published game without scores has an empty average and a zero count."""
    card = await get_game_card(catalog.disco.uuid)

    assert card.game.uuid == catalog.disco.uuid
    assert card.summary.users_score is None
    assert card.summary.ratings_count == 0
    assert card.user_score is None
    assert card.list_status is None


async def test_get_game_card_averages_scores_from_several_users(
    di_container: DIContainer,
    registered_user: User,
    catalog: Catalog,
) -> None:
    """The card average is the mean of every user's score for that game."""
    scores = [8, 9]
    await add_to_completed(registered_user, AddUserGameData(game_uuid=catalog.planescape.uuid))
    await set_rating(registered_user, catalog.planescape.uuid, SetRatingData(score=scores[0]))
    await di_container.auth_service().register_user(
        CreateUserData(email='other@mail.ru', password='secret', nickname='other'),
    )
    other = await InMemUserRepo().get_by_email('other@mail.ru')
    assert other is not None
    await add_to_completed(other, AddUserGameData(game_uuid=catalog.planescape.uuid))
    await set_rating(other, catalog.planescape.uuid, SetRatingData(score=scores[1]))

    card = await get_game_card(catalog.planescape.uuid)

    assert card.summary.ratings_count == len(scores)
    assert card.summary.users_score == sum(scores) / len(scores)
    assert card.user_score is None
    assert card.list_status is None


async def test_get_game_card_returns_only_the_callers_score(
    di_container: DIContainer,
    registered_user: User,
    catalog: Catalog,
) -> None:
    """The card shows the caller's score and leaves another user's score out of that field."""
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
    before_other_rates = await get_game_card(catalog.planescape.uuid, other)

    await set_rating(other, catalog.planescape.uuid, other_score)
    owner_card = await get_game_card(catalog.planescape.uuid, registered_user)
    other_card = await get_game_card(catalog.planescape.uuid, other)
    anonymous = await get_game_card(catalog.planescape.uuid)

    assert before_other_rates.user_score is None
    assert owner_card.user_score == owner_score.score
    assert other_card.user_score == other_score.score
    assert anonymous.user_score is None
    assert owner_card.summary.users_score == (owner_score.score + other_score.score) / 2


async def test_get_game_card_returns_the_callers_list_status(
    di_container: DIContainer,
    registered_user: User,
    catalog: Catalog,
) -> None:
    """The card shows the caller's list status and leaves another user's status out of that field."""
    await add_to_backlog(registered_user, AddUserGameData(game_uuid=catalog.planescape.uuid))
    await add_to_completed(registered_user, AddUserGameData(game_uuid=catalog.disco.uuid))
    await add_to_backlog(registered_user, AddUserGameData(game_uuid=catalog.hidden.uuid))
    await di_container.auth_service().register_user(
        CreateUserData(email='other@mail.ru', password='secret', nickname='other'),
    )
    other = await InMemUserRepo().get_by_email('other@mail.ru')
    assert other is not None

    backlog = await get_game_card(catalog.planescape.uuid, registered_user)
    completed = await get_game_card(catalog.disco.uuid, registered_user)
    absent = await get_game_card(catalog.torment.uuid, registered_user)
    anonymous = await get_game_card(catalog.planescape.uuid)
    stranger = await get_game_card(catalog.planescape.uuid, other)

    assert backlog.list_status == UserGameStatus.backlog
    assert completed.list_status == UserGameStatus.completed
    assert absent.list_status is None
    assert anonymous.list_status is None
    assert stranger.list_status is None
    with pytest.raises(GameNotFoundError, match=f'Game with uuid={catalog.hidden.uuid} not found'):
        await get_game_card(catalog.hidden.uuid, registered_user)


async def test_get_game_card_hides_an_unpublished_game(catalog: Catalog) -> None:
    """A hidden game stays out of the catalog card."""
    with pytest.raises(GameNotFoundError, match=f'Game with uuid={catalog.hidden.uuid} not found'):
        await get_game_card(catalog.hidden.uuid)
