from http import HTTPStatus
from uuid import UUID

from httpx import AsyncClient

from adapters.databases.in_memory.repositories.email_confirmations.email_confirmation import InMemEmailConfirmationRepo
from adapters.databases.in_memory.repositories.users.user import InMemUserRepo
from tests.fixtures.game import Catalog


async def test_remove_from_list_requires_a_token(client: AsyncClient, catalog: Catalog) -> None:
    """A request without a token is rejected."""
    response = await client.delete(f'/users/me/games/{catalog.planescape.uuid}')

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Not authenticated'}


async def test_remove_from_list_deletes_a_backlog_game(
    client: AsyncClient,
    access_token: str,
    catalog: Catalog,
) -> None:
    """The current user removes a backlog game and then sees an empty backlog."""
    headers = {'Authorization': f'Bearer {access_token}'}
    created = await client.post(
        '/users/me/backlog',
        headers=headers,
        json={'game_uuid': str(catalog.planescape.uuid)},
    )
    response = await client.delete(f'/users/me/games/{catalog.planescape.uuid}', headers=headers)
    me = await client.get('/users/me', headers=headers)
    backlog = await client.get(f'/users/{me.json()["uuid"]}/backlog')

    assert created.status_code == HTTPStatus.CREATED
    assert response.status_code == HTTPStatus.NO_CONTENT
    assert response.content == b''
    assert backlog.json() == {'items': [], 'total': 0}


async def test_remove_from_list_deletes_a_completed_game(
    client: AsyncClient,
    access_token: str,
    catalog: Catalog,
) -> None:
    """The current user removes a completed game and then sees an empty completed list."""
    headers = {'Authorization': f'Bearer {access_token}'}
    created = await client.post(
        '/users/me/completed',
        headers=headers,
        json={'game_uuid': str(catalog.torment.uuid)},
    )
    response = await client.delete(f'/users/me/games/{catalog.torment.uuid}', headers=headers)
    me = await client.get('/users/me', headers=headers)
    completed = await client.get(f'/users/{me.json()["uuid"]}/completed')

    assert created.status_code == HTTPStatus.CREATED
    assert response.status_code == HTTPStatus.NO_CONTENT
    assert completed.json() == {'items': [], 'total': 0}


async def test_remove_from_list_missing_row_returns_404(
    client: AsyncClient,
    access_token: str,
    catalog: Catalog,
) -> None:
    """A game that is not in the current user's lists returns 404."""
    response = await client.delete(
        f'/users/me/games/{catalog.disco.uuid}',
        headers={'Authorization': f'Bearer {access_token}'},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': f'Game with uuid={catalog.disco.uuid} is not listed'}


async def test_remove_from_list_unknown_game_returns_404(client: AsyncClient, access_token: str) -> None:
    """An unknown game returns 404."""
    missing_game_uuid = UUID('00000000-0000-0000-0000-000000000099')

    response = await client.delete(
        f'/users/me/games/{missing_game_uuid}',
        headers={'Authorization': f'Bearer {access_token}'},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': f'Game with uuid={missing_game_uuid} not found'}


async def test_remove_from_list_does_not_delete_another_users_row(
    client: AsyncClient,
    access_token: str,
    catalog: Catalog,
) -> None:
    """Another user receives 404 and the owner's row stays in the backlog."""
    owner_headers = {'Authorization': f'Bearer {access_token}'}
    created = await client.post(
        '/users/me/backlog',
        headers=owner_headers,
        json={'game_uuid': str(catalog.planescape.uuid)},
    )
    registered = await client.post(
        '/auth/register',
        json={'email': 'other@mail.ru', 'password': 'secret', 'nickname': 'other'},
    )
    other = await InMemUserRepo().get_by_email('other@mail.ru')
    assert other is not None
    confirmation = next(item for item in InMemEmailConfirmationRepo.DB.values() if item.user_id == other.id)
    confirmed = await client.post('/auth/confirm', json={'token': confirmation.token})
    logged_in = await client.post('/auth/login', json={'email': 'other@mail.ru', 'password': 'secret'})
    response = await client.delete(
        f'/users/me/games/{catalog.planescape.uuid}',
        headers={'Authorization': f'Bearer {logged_in.json()["access_token"]}'},
    )
    me = await client.get('/users/me', headers=owner_headers)
    backlog = await client.get(f'/users/{me.json()["uuid"]}/backlog')

    assert created.status_code == HTTPStatus.CREATED
    assert registered.status_code == HTTPStatus.CREATED
    assert confirmed.status_code == HTTPStatus.NO_CONTENT
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': f'Game with uuid={catalog.planescape.uuid} is not listed'}
    assert [item['title'] for item in backlog.json()['items']] == [catalog.planescape.title]


async def test_remove_from_list_rejects_a_non_uuid(client: AsyncClient, access_token: str) -> None:
    """A non-uuid path is rejected before lookup."""
    response = await client.delete(
        '/users/me/games/not-a-uuid',
        headers={'Authorization': f'Bearer {access_token}'},
    )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
