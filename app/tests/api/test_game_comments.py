from http import HTTPStatus
from uuid import UUID

from httpx import AsyncClient

from tests.fixtures.game import Catalog


async def test_get_comments_returns_an_empty_page(client: AsyncClient, catalog: Catalog) -> None:
    """A published game without comments has an empty page, and no token is sent."""
    response = await client.get(f'/games/{catalog.disco.uuid}/comments')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'items': [], 'total': 0}


async def test_get_comments_returns_comments_in_creation_order(
    client: AsyncClient,
    access_token: str,
    catalog: Catalog,
) -> None:
    """Comments are returned without a token, in the order they were created, with the author."""
    headers = {'Authorization': f'Bearer {access_token}'}
    first = await client.post(
        f'/games/{catalog.disco.uuid}/comments',
        headers=headers,
        json={'text': 'Earlier'},
    )
    second = await client.post(
        f'/games/{catalog.disco.uuid}/comments',
        headers=headers,
        json={'text': 'Later'},
    )
    page = await client.get(f'/games/{catalog.disco.uuid}/comments')
    created = [first.json(), second.json()]

    assert first.status_code == HTTPStatus.CREATED
    assert second.status_code == HTTPStatus.CREATED
    assert page.status_code == HTTPStatus.OK
    assert page.json() == {'items': created, 'total': len(created)}


async def test_get_comments_returns_the_requested_slice(
    client: AsyncClient,
    access_token: str,
    catalog: Catalog,
) -> None:
    """Offset and limit cut the page and leave the total unchanged."""
    headers = {'Authorization': f'Bearer {access_token}'}
    await client.post(
        f'/games/{catalog.disco.uuid}/comments',
        headers=headers,
        json={'text': 'Earlier'},
    )
    second = await client.post(
        f'/games/{catalog.disco.uuid}/comments',
        headers=headers,
        json={'text': 'Later'},
    )
    created = ['Earlier', 'Later']
    page = await client.get(f'/games/{catalog.disco.uuid}/comments', params={'limit': 1, 'offset': 1})

    assert page.status_code == HTTPStatus.OK
    assert page.json()['items'] == [second.json()]
    assert page.json()['total'] == len(created)


async def test_get_comments_unknown_game_returns_404(client: AsyncClient) -> None:
    """An unknown game returns 404."""
    missing_game_uuid = UUID('00000000-0000-0000-0000-000000000099')

    response = await client.get(f'/games/{missing_game_uuid}/comments')

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': f'Game with uuid={missing_game_uuid} not found'}


async def test_get_comments_hidden_game_returns_404(client: AsyncClient, catalog: Catalog) -> None:
    """A hidden game returns 404."""
    response = await client.get(f'/games/{catalog.hidden.uuid}/comments')

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': f'Game with uuid={catalog.hidden.uuid} not found'}
