from http import HTTPStatus
from uuid import uuid4

from httpx import AsyncClient


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


async def test_public_profile_missing_user_returns_404(client: AsyncClient) -> None:
    """An unknown user uuid returns 404."""
    missing = uuid4()

    response = await client.get(f'/users/{missing}')

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': f'User with uuid={missing} not found'}
