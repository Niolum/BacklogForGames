from datetime import UTC, datetime
from http import HTTPStatus
from uuid import UUID

from httpx import AsyncClient

from adapters.databases.in_memory.repositories.user_games.user_game import InMemUserGameRepo
from adapters.databases.in_memory.repositories.users.user import InMemUserRepo
from domain.models import UserGame, UserGameStatus
from tests.fixtures.game import Catalog


async def test_add_to_backlog_requires_a_token(client: AsyncClient, catalog: Catalog) -> None:
    """A request without a token is rejected."""
    response = await client.post('/users/me/backlog', json={'game_uuid': str(catalog.planescape.uuid)})

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Not authenticated'}


async def test_add_to_backlog_returns_created(client: AsyncClient, access_token: str, catalog: Catalog) -> None:
    """The current user adds a game and then sees it in the backlog."""
    response = await client.post(
        '/users/me/backlog',
        headers={'Authorization': f'Bearer {access_token}'},
        json={'game_uuid': str(catalog.planescape.uuid)},
    )
    me = await client.get('/users/me', headers={'Authorization': f'Bearer {access_token}'})
    backlog = await client.get(f'/users/{me.json()["uuid"]}/backlog')

    assert response.status_code == HTTPStatus.CREATED
    assert response.content == b''
    assert backlog.status_code == HTTPStatus.OK
    assert [item['title'] for item in backlog.json()['items']] == [catalog.planescape.title]
    assert backlog.json()['total'] == 1


async def test_add_to_backlog_unknown_game_returns_404(client: AsyncClient, access_token: str) -> None:
    """An unknown game returns 404."""
    missing_game_uuid = UUID('00000000-0000-0000-0000-000000000099')

    response = await client.post(
        '/users/me/backlog',
        headers={'Authorization': f'Bearer {access_token}'},
        json={'game_uuid': str(missing_game_uuid)},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': f'Game with uuid={missing_game_uuid} not found'}


async def test_add_to_backlog_already_listed_returns_409(
    client: AsyncClient,
    access_token: str,
    catalog: Catalog,
) -> None:
    """A game already in the backlog or in completed games returns 409."""
    headers = {'Authorization': f'Bearer {access_token}'}
    created = await client.post(
        '/users/me/backlog',
        headers=headers,
        json={'game_uuid': str(catalog.planescape.uuid)},
    )
    again = await client.post(
        '/users/me/backlog',
        headers=headers,
        json={'game_uuid': str(catalog.planescape.uuid)},
    )

    user = await InMemUserRepo().get_by_email('user@mail.ru')
    assert user is not None
    await InMemUserGameRepo().create(
        UserGame(
            id=2,
            user_id=user.id,
            game_id=catalog.torment.id,
            status=UserGameStatus.completed,
            created_at=datetime(2026, 10, 14, tzinfo=UTC),
            completed_at=datetime(2026, 10, 14, 15, tzinfo=UTC),
        ),
    )
    completed = await client.post(
        '/users/me/backlog',
        headers=headers,
        json={'game_uuid': str(catalog.torment.uuid)},
    )

    assert created.status_code == HTTPStatus.CREATED
    assert again.status_code == HTTPStatus.CONFLICT
    assert again.json() == {'detail': f'Game with uuid={catalog.planescape.uuid} is already listed'}
    assert completed.status_code == HTTPStatus.CONFLICT
    assert completed.json() == {'detail': f'Game with uuid={catalog.torment.uuid} is already listed'}


async def test_add_to_backlog_rejects_a_missing_game_uuid(client: AsyncClient, access_token: str) -> None:
    """A body without game_uuid is rejected before lookup."""
    response = await client.post(
        '/users/me/backlog',
        headers={'Authorization': f'Bearer {access_token}'},
        json={},
    )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
