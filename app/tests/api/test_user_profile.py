from http import HTTPStatus
from uuid import uuid4

from httpx import AsyncClient

from tests.fixtures.game import Catalog


async def test_me_returns_private_profile(client: AsyncClient, access_token: str) -> None:
    """The current user sees their email and not the password."""
    response = await client.get('/users/me', headers={'Authorization': f'Bearer {access_token}'})

    assert response.status_code == HTTPStatus.OK
    body = response.json()
    assert body['nickname'] == 'nick'
    assert body['email'] == 'user@mail.ru'
    assert body['email_confirmed'] is True
    assert body['date_birth'] is None
    assert body['about'] is None
    assert body['avatar_url'] is None
    assert body['backlog_count'] == 0
    assert body['completed_count'] == 0
    assert 'is_admin' not in body
    assert 'password' not in body
    assert body['created_at']


async def test_public_profile_hides_email_and_password(client: AsyncClient, access_token: str) -> None:
    """Anyone can read a profile, and it omits email and password."""
    me = await client.get('/users/me', headers={'Authorization': f'Bearer {access_token}'})
    user_uuid = me.json()['uuid']

    response = await client.get(f'/users/{user_uuid}')

    assert response.status_code == HTTPStatus.OK
    body = response.json()
    assert body['uuid'] == user_uuid
    assert body['nickname'] == 'nick'
    assert body['avatar_url'] is None
    assert body['backlog_count'] == 0
    assert body['completed_count'] == 0
    assert 'email' not in body
    assert 'password' not in body
    assert 'is_admin' not in body


async def test_profile_counts_skip_a_hidden_game(
    client: AsyncClient,
    access_token: str,
    catalog: Catalog,
) -> None:
    """A hidden game stays on the list and is left out of both profiles."""
    headers = {'Authorization': f'Bearer {access_token}'}
    backlog = await client.post(
        '/users/me/backlog',
        headers=headers,
        json={'game_uuid': str(catalog.hidden.uuid)},
    )
    completed = await client.post(
        '/users/me/completed',
        headers=headers,
        json={'game_uuid': str(catalog.disco.uuid)},
    )
    me = await client.get('/users/me', headers=headers)
    public = await client.get(f'/users/{me.json()["uuid"]}')
    published = [catalog.disco]
    hidden_list = await client.get(f'/users/{me.json()["uuid"]}/backlog')

    assert backlog.status_code == HTTPStatus.CREATED
    assert completed.status_code == HTTPStatus.CREATED
    assert me.status_code == HTTPStatus.OK
    assert me.json()['backlog_count'] == 0
    assert me.json()['completed_count'] == len(published)
    assert public.status_code == HTTPStatus.OK
    assert public.json()['backlog_count'] == me.json()['backlog_count']
    assert public.json()['completed_count'] == me.json()['completed_count']
    assert hidden_list.json()['total'] == len([catalog.hidden])
    assert 'is_admin' not in public.json()


async def test_public_profile_missing_user_returns_404(client: AsyncClient) -> None:
    """An unknown user uuid returns 404."""
    missing = uuid4()

    response = await client.get(f'/users/{missing}')

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': f'User with uuid={missing} not found'}
