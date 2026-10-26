from adapters.databases.in_memory.repositories.users.user import InMemUserRepo
from deps.container import DIContainer
from domain.models import User
from domain.services import AddUserGameData, SetRatingData
from domain.services.auth.types import CreateUserData
from domain.use_cases import add_to_backlog, add_to_completed, get_user_backlog, get_user_completed, set_rating
from tests.fixtures.game import Catalog


async def test_get_user_completed_returns_the_owners_score(
    di_container: DIContainer,
    registered_user: User,
    catalog: Catalog,
) -> None:
    """The completed page shows the list owner's score, including a hidden game, and omits another user's score."""
    owner_score = SetRatingData(score=7)
    hidden_score = SetRatingData(score=4)
    other_score = SetRatingData(score=9)
    await add_to_completed(registered_user, AddUserGameData(game_uuid=catalog.disco.uuid))
    await add_to_completed(registered_user, AddUserGameData(game_uuid=catalog.planescape.uuid))
    await set_rating(registered_user, catalog.planescape.uuid, owner_score)
    await add_to_completed(registered_user, AddUserGameData(game_uuid=catalog.hidden.uuid))
    await set_rating(registered_user, catalog.hidden.uuid, hidden_score)
    await add_to_backlog(registered_user, AddUserGameData(game_uuid=catalog.torment.uuid))
    await di_container.auth_service().register_user(
        CreateUserData(email='other@mail.ru', password='secret', nickname='other'),
    )
    other = await InMemUserRepo().get_by_email('other@mail.ru')
    assert other is not None
    await add_to_completed(other, AddUserGameData(game_uuid=catalog.planescape.uuid))
    await set_rating(other, catalog.planescape.uuid, other_score)

    page = await get_user_completed(registered_user.uuid, limit=20, offset=0)
    other_page = await get_user_completed(other.uuid, limit=20, offset=0)
    backlog = await get_user_backlog(registered_user.uuid, limit=20, offset=0)
    titles = [catalog.disco.title, catalog.hidden.title, catalog.planescape.title]

    assert [item.game.title for item in page.items] == titles
    assert [item.user_score for item in page.items] == [None, hidden_score.score, owner_score.score]
    assert page.total == len(titles)
    assert [item.user_score for item in other_page.items] == [other_score.score]
    assert [item.title for item in backlog.items] == [catalog.torment.title]
