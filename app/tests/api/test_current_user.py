from http import HTTPStatus

from httpx import AsyncClient


async def test_current_user_requires_token(client: AsyncClient) -> None:
    """A request without Authorization receives 401."""
    response = await client.get('/users/me')

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Not authenticated'}


async def test_current_user_rejects_invalid_token(client: AsyncClient) -> None:
    """A request with a broken bearer token receives 401."""
    response = await client.get('/users/me', headers={'Authorization': 'Bearer not-a-token'})

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Invalid token'}


async def test_current_user_rejects_non_bearer_scheme(client: AsyncClient, access_token: str) -> None:
    """A token sent with another scheme receives 401."""
    response = await client.get('/users/me', headers={'Authorization': f'Token {access_token}'})

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Not authenticated'}


async def test_current_user_accepts_bearer_token(client: AsyncClient, access_token: str) -> None:
    """A valid bearer token passes the current-user dependency."""
    response = await client.get('/users/me', headers={'Authorization': f'Bearer {access_token}'})

    assert response.status_code == HTTPStatus.NO_CONTENT
    assert response.content == b''
