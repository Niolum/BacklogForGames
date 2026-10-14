from http import HTTPStatus
from uuid import UUID

from httpx import AsyncClient

from tests.fixtures.game import Catalog


async def test_add_to_completed_requires_a_token(client: AsyncClient, catalog: Catalog) -> None:
    """A request without a token is rejected."""
    response = await client.post('/users/me/completed', json={'game_uuid': str(catalog.planescape.uuid)})

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Not authenticated'}


async def test_add_to_completed_returns_created(client: AsyncClient, access_token: str, catalog: Catalog) -> None:
    """The current user marks a game completed and then sees it only in that list."""
    headers = {'Authorization': f'Bearer {access_token}'}
    response = await client.post(
        '/users/me/completed',
        headers=headers,
        json={'game_uuid': str(catalog.disco.uuid)},
    )
    me = await client.get('/users/me', headers=headers)
    user_uuid = me.json()['uuid']
    backlog = await client.get(f'/users/{user_uuid}/backlog')
    completed = await client.get(f'/users/{user_uuid}/completed')

    assert response.status_code == HTTPStatus.CREATED
    assert response.content == b''
    assert backlog.json() == {'items': [], 'total': 0}
    assert [item['title'] for item in completed.json()['items']] == [catalog.disco.title]
    assert completed.json()['total'] == 1


async def test_add_to_completed_moves_a_backlog_game(client: AsyncClient, access_token: str, catalog: Catalog) -> None:
    """A game in the backlog moves to completed and disappears from the backlog."""
    headers = {'Authorization': f'Bearer {access_token}'}
    created = await client.post(
        '/users/me/backlog',
        headers=headers,
        json={'game_uuid': str(catalog.planescape.uuid)},
    )
    moved = await client.post(
        '/users/me/completed',
        headers=headers,
        json={'game_uuid': str(catalog.planescape.uuid)},
    )
    me = await client.get('/users/me', headers=headers)
    user_uuid = me.json()['uuid']
    backlog = await client.get(f'/users/{user_uuid}/backlog')
    completed = await client.get(f'/users/{user_uuid}/completed')

    assert created.status_code == HTTPStatus.CREATED
    assert moved.status_code == HTTPStatus.CREATED
    assert backlog.json() == {'items': [], 'total': 0}
    assert [item['title'] for item in completed.json()['items']] == [catalog.planescape.title]


async def test_add_to_completed_already_completed_returns_409(
    client: AsyncClient,
    access_token: str,
    catalog: Catalog,
) -> None:
    """A game that is already completed returns 409."""
    headers = {'Authorization': f'Bearer {access_token}'}
    body = {'game_uuid': str(catalog.torment.uuid)}
    created = await client.post('/users/me/completed', headers=headers, json=body)
    again = await client.post('/users/me/completed', headers=headers, json=body)

    assert created.status_code == HTTPStatus.CREATED
    assert again.status_code == HTTPStatus.CONFLICT
    assert again.json() == {'detail': f'Game with uuid={catalog.torment.uuid} is already completed'}


async def test_add_to_completed_unknown_game_returns_404(client: AsyncClient, access_token: str) -> None:
    """An unknown game returns 404."""
    missing_game_uuid = UUID('00000000-0000-0000-0000-000000000099')

    response = await client.post(
        '/users/me/completed',
        headers={'Authorization': f'Bearer {access_token}'},
        json={'game_uuid': str(missing_game_uuid)},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': f'Game with uuid={missing_game_uuid} not found'}


async def test_add_to_completed_rejects_a_missing_game_uuid(client: AsyncClient, access_token: str) -> None:
    """A body without game_uuid is rejected before lookup."""
    response = await client.post(
        '/users/me/completed',
        headers={'Authorization': f'Bearer {access_token}'},
        json={},
    )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
