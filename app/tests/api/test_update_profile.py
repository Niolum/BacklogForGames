from http import HTTPStatus

from httpx import AsyncClient

from adapters.databases.in_memory.repositories.users.user import InMemUserRepo


async def test_patch_me_updates_profile(client: AsyncClient, access_token: str) -> None:
    """The token owner changes nickname, date of birth and about."""
    response = await client.patch(
        '/users/me',
        headers={'Authorization': f'Bearer {access_token}'},
        json={'nickname': 'renamed', 'date_birth': '1990-01-02', 'about': 'hello'},
    )

    assert response.status_code == HTTPStatus.OK
    body = response.json()
    assert body['nickname'] == 'renamed'
    assert body['date_birth'] == '1990-01-02'
    assert body['about'] == 'hello'
    assert body['email'] == 'user@mail.ru'
    assert body['email_confirmed'] is True

    public = await client.get(f'/users/{body["uuid"]}')
    assert public.status_code == HTTPStatus.OK
    assert public.json()['nickname'] == 'renamed'
    assert public.json()['about'] == 'hello'


async def test_patch_me_keeps_omitted_fields(client: AsyncClient, access_token: str) -> None:
    """A field missing from the body stays as it was."""
    first = await client.patch(
        '/users/me',
        headers={'Authorization': f'Bearer {access_token}'},
        json={'nickname': 'renamed', 'date_birth': '1990-01-02', 'about': 'hello'},
    )
    assert first.status_code == HTTPStatus.OK

    response = await client.patch(
        '/users/me',
        headers={'Authorization': f'Bearer {access_token}'},
        json={'about': 'updated'},
    )

    assert response.status_code == HTTPStatus.OK
    body = response.json()
    assert body['nickname'] == 'renamed'
    assert body['date_birth'] == '1990-01-02'
    assert body['about'] == 'updated'
    assert body['email'] == 'user@mail.ru'


async def test_patch_me_clears_optional_fields(client: AsyncClient, access_token: str) -> None:
    """An explicit null clears date of birth and about."""
    filled = await client.patch(
        '/users/me',
        headers={'Authorization': f'Bearer {access_token}'},
        json={'date_birth': '1990-01-02', 'about': 'hello'},
    )
    assert filled.status_code == HTTPStatus.OK

    response = await client.patch(
        '/users/me',
        headers={'Authorization': f'Bearer {access_token}'},
        json={'date_birth': None, 'about': None},
    )

    assert response.status_code == HTTPStatus.OK
    body = response.json()
    assert body['nickname'] == 'nick'
    assert body['date_birth'] is None
    assert body['about'] is None


async def test_patch_me_rejects_taken_nickname(client: AsyncClient, access_token: str) -> None:
    """A nickname that belongs to someone else returns 409 and leaves the profile unchanged."""
    other = await client.post(
        '/auth/register',
        json={'email': 'other@mail.ru', 'password': 'secret', 'nickname': 'other'},
    )
    assert other.status_code == HTTPStatus.CREATED

    response = await client.patch(
        '/users/me',
        headers={'Authorization': f'Bearer {access_token}'},
        json={'nickname': 'other'},
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'User with nickname=other already exists'}
    me = await client.get('/users/me', headers={'Authorization': f'Bearer {access_token}'})
    assert me.json()['nickname'] == 'nick'
    stored_other = await InMemUserRepo().get_by_email('other@mail.ru')
    assert stored_other is not None
    assert stored_other.nickname == 'other'


async def test_patch_me_accepts_own_nickname(client: AsyncClient, access_token: str) -> None:
    """Saving the current nickname is not a conflict."""
    response = await client.patch(
        '/users/me',
        headers={'Authorization': f'Bearer {access_token}'},
        json={'nickname': 'nick', 'about': 'same nick'},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json()['nickname'] == 'nick'
    assert response.json()['about'] == 'same nick'


async def test_patch_me_requires_token(client: AsyncClient) -> None:
    """A profile change without a token receives 401."""
    response = await client.patch('/users/me', json={'about': 'hello'})

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Not authenticated'}


async def test_patch_me_rejects_null_nickname(client: AsyncClient, access_token: str) -> None:
    """An explicit null nickname is rejected and the stored nickname stays."""
    response = await client.patch(
        '/users/me',
        headers={'Authorization': f'Bearer {access_token}'},
        json={'nickname': None},
    )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    stored = await InMemUserRepo().get_by_email('user@mail.ru')
    assert stored is not None
    assert stored.nickname == 'nick'


async def test_patch_me_rejects_empty_nickname(client: AsyncClient, access_token: str) -> None:
    """An empty nickname is rejected and the stored nickname stays."""
    response = await client.patch(
        '/users/me',
        headers={'Authorization': f'Bearer {access_token}'},
        json={'nickname': ''},
    )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    stored = await InMemUserRepo().get_by_email('user@mail.ru')
    assert stored is not None
    assert stored.nickname == 'nick'
