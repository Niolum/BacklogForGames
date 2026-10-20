from http import HTTPStatus
from uuid import UUID

from httpx import AsyncClient

from tests.fixtures.game import Catalog


async def test_set_rating_requires_a_token(client: AsyncClient, catalog: Catalog) -> None:
    """A request without a token is rejected."""
    response = await client.put(f'/games/{catalog.disco.uuid}/rating', json={'score': 8})

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Not authenticated'}


async def test_set_rating_returns_the_saved_score(client: AsyncClient, access_token: str, catalog: Catalog) -> None:
    """The current user scores a completed game and receives that score."""
    headers = {'Authorization': f'Bearer {access_token}'}
    score = 8
    completed = await client.post(
        '/users/me/completed',
        headers=headers,
        json={'game_uuid': str(catalog.disco.uuid)},
    )
    response = await client.put(
        f'/games/{catalog.disco.uuid}/rating',
        headers=headers,
        json={'score': score},
    )

    assert completed.status_code == HTTPStatus.CREATED
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'score': score}


async def test_set_rating_unknown_game_returns_404(client: AsyncClient, access_token: str) -> None:
    """An unknown game returns 404."""
    missing_game_uuid = UUID('00000000-0000-0000-0000-000000000099')

    response = await client.put(
        f'/games/{missing_game_uuid}/rating',
        headers={'Authorization': f'Bearer {access_token}'},
        json={'score': 8},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': f'Game with uuid={missing_game_uuid} not found'}


async def test_set_rating_rejects_a_score_outside_the_scale(
    client: AsyncClient,
    access_token: str,
    catalog: Catalog,
) -> None:
    """A score below 1 or above 10 is rejected before lookup."""
    headers = {'Authorization': f'Bearer {access_token}'}
    low = await client.put(f'/games/{catalog.disco.uuid}/rating', headers=headers, json={'score': 0})
    high = await client.put(f'/games/{catalog.disco.uuid}/rating', headers=headers, json={'score': 11})
    missing = await client.put(f'/games/{catalog.disco.uuid}/rating', headers=headers, json={})

    assert low.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    assert high.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    assert missing.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


async def test_set_rating_rejects_a_game_that_is_not_completed(
    client: AsyncClient,
    access_token: str,
    catalog: Catalog,
) -> None:
    """A backlog game and a game absent from the lists return 409."""
    headers = {'Authorization': f'Bearer {access_token}'}
    created = await client.post(
        '/users/me/backlog',
        headers=headers,
        json={'game_uuid': str(catalog.planescape.uuid)},
    )
    backlog = await client.put(
        f'/games/{catalog.planescape.uuid}/rating',
        headers=headers,
        json={'score': 8},
    )
    absent = await client.put(
        f'/games/{catalog.disco.uuid}/rating',
        headers=headers,
        json={'score': 8},
    )

    assert created.status_code == HTTPStatus.CREATED
    assert backlog.status_code == HTTPStatus.CONFLICT
    assert backlog.json() == {'detail': f'Game with uuid={catalog.planescape.uuid} is not completed'}
    assert absent.status_code == HTTPStatus.CONFLICT
    assert absent.json() == {'detail': f'Game with uuid={catalog.disco.uuid} is not completed'}
