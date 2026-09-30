from http import HTTPStatus

from httpx import AsyncClient

from adapters.databases.in_memory.repositories.users.user import InMemUserRepo
from config import storage_settings
from domain.constants import AVATAR_MAX_BYTES


async def test_upload_avatar_returns_it_in_the_profile(client: AsyncClient, access_token: str) -> None:
    """The current user stores an avatar, and both profiles return its path."""
    response = await client.post(
        '/users/me/avatar',
        headers={'Authorization': f'Bearer {access_token}'},
        files={'file': ('avatar.png', b'png-bytes', 'image/png')},
    )

    assert response.status_code == HTTPStatus.OK
    body = response.json()
    assert body['avatar_url'].endswith('.png')
    assert body['email'] == 'user@mail.ru'
    stored = storage_settings.local_root / body['avatar_url']
    assert stored.read_bytes() == b'png-bytes'

    me = await client.get('/users/me', headers={'Authorization': f'Bearer {access_token}'})
    assert me.json()['avatar_url'] == body['avatar_url']
    public = await client.get(f'/users/{body["uuid"]}')
    assert public.json()['avatar_url'] == body['avatar_url']


async def test_upload_avatar_replaces_the_previous_file(client: AsyncClient, access_token: str) -> None:
    """A new avatar removes the previous file and keeps the other user unchanged."""
    other = await client.post(
        '/auth/register',
        json={'email': 'other@mail.ru', 'password': 'secret', 'nickname': 'other'},
    )
    assert other.status_code == HTTPStatus.CREATED
    headers = {'Authorization': f'Bearer {access_token}'}

    first = await client.post(
        '/users/me/avatar',
        headers=headers,
        files={'file': ('avatar.png', b'png-bytes', 'image/png')},
    )
    assert first.status_code == HTTPStatus.OK
    previous = storage_settings.local_root / first.json()['avatar_url']

    second = await client.post(
        '/users/me/avatar',
        headers=headers,
        files={'file': ('avatar.gif', b'gif-bytes', 'image/gif')},
    )

    assert second.status_code == HTTPStatus.OK
    assert second.json()['avatar_url'].endswith('.gif')
    assert not previous.exists()
    assert (storage_settings.local_root / second.json()['avatar_url']).read_bytes() == b'gif-bytes'
    stored_other = await InMemUserRepo().get_by_email('other@mail.ru')
    assert stored_other is not None
    assert stored_other.avatar_url is None


async def test_delete_avatar_clears_the_profile(client: AsyncClient, access_token: str) -> None:
    """Deleting the avatar removes the file and clears the profile field."""
    headers = {'Authorization': f'Bearer {access_token}'}
    uploaded = await client.post(
        '/users/me/avatar',
        headers=headers,
        files={'file': ('avatar.png', b'png-bytes', 'image/png')},
    )
    assert uploaded.status_code == HTTPStatus.OK
    stored = storage_settings.local_root / uploaded.json()['avatar_url']

    response = await client.delete('/users/me/avatar', headers=headers)

    assert response.status_code == HTTPStatus.NO_CONTENT
    assert not stored.exists()
    me = await client.get('/users/me', headers=headers)
    assert me.json()['avatar_url'] is None


async def test_delete_avatar_without_file_returns_204(client: AsyncClient, access_token: str) -> None:
    """Deleting an avatar that was never set still returns 204."""
    response = await client.delete(
        '/users/me/avatar',
        headers={'Authorization': f'Bearer {access_token}'},
    )

    assert response.status_code == HTTPStatus.NO_CONTENT


async def test_avatar_requires_token(client: AsyncClient) -> None:
    """Upload and delete without a token receive 401."""
    upload = await client.post(
        '/users/me/avatar',
        files={'file': ('avatar.png', b'png-bytes', 'image/png')},
    )
    delete = await client.delete('/users/me/avatar')

    assert upload.status_code == HTTPStatus.UNAUTHORIZED
    assert upload.json() == {'detail': 'Not authenticated'}
    assert delete.status_code == HTTPStatus.UNAUTHORIZED
    assert delete.json() == {'detail': 'Not authenticated'}


async def test_upload_avatar_rejects_empty_and_unsupported_file(client: AsyncClient, access_token: str) -> None:
    """An empty file and an unsupported type are rejected before anything is stored."""
    headers = {'Authorization': f'Bearer {access_token}'}
    empty = await client.post(
        '/users/me/avatar',
        headers=headers,
        files={'file': ('avatar.png', b'', 'image/png')},
    )
    unsupported = await client.post(
        '/users/me/avatar',
        headers=headers,
        files={'file': ('notes.txt', b'hello', 'text/plain')},
    )

    assert empty.status_code == HTTPStatus.BAD_REQUEST
    assert empty.json() == {'detail': 'Avatar file is empty'}
    assert unsupported.status_code == HTTPStatus.BAD_REQUEST
    assert unsupported.json() == {'detail': 'Unsupported avatar file type'}
    assert list(storage_settings.local_root.iterdir()) == []


async def test_upload_avatar_rejects_oversized_file(client: AsyncClient, access_token: str) -> None:
    """A file above the size limit is rejected."""
    response = await client.post(
        '/users/me/avatar',
        headers={'Authorization': f'Bearer {access_token}'},
        files={'file': ('avatar.png', b'a' * (AVATAR_MAX_BYTES + 1), 'image/png')},
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json() == {'detail': 'Avatar file is too large'}
    assert list(storage_settings.local_root.iterdir()) == []
