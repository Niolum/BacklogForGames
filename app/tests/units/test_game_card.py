import pytest

from adapters.databases.in_memory.repositories.users.user import InMemUserRepo
from deps.container import DIContainer
from domain.exceptions import GameNotFoundError
from domain.models import User
from domain.services import AddUserGameData, SetRatingData
from domain.services.auth.types import CreateUserData
from domain.use_cases import add_to_completed, get_game_card, set_rating
from tests.fixtures.game import Catalog


async def test_get_game_card_has_no_scores_yet(catalog: Catalog) -> None:
    """A published game without scores has an empty average and a zero count."""
    card = await get_game_card(catalog.disco.uuid)

    assert card.game.uuid == catalog.disco.uuid
    assert card.summary.users_score is None
    assert card.summary.ratings_count == 0


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


async def test_get_game_card_hides_an_unpublished_game(catalog: Catalog) -> None:
    """A hidden game stays out of the catalog card."""
    with pytest.raises(GameNotFoundError, match=f'Game with uuid={catalog.hidden.uuid} not found'):
        await get_game_card(catalog.hidden.uuid)
