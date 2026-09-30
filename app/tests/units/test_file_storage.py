from pathlib import Path

import pytest

from adapters.databases.in_memory.repositories.users.user import InMemUserRepo
from adapters.storage import LocalFileStorage, S3FileStorage
from dependencies.container import DIContainer
from domain.exceptions import BadRequestError
from domain.services.auth.types import CreateUserData


async def test_local_storage_saves_and_deletes(tmp_path: Path) -> None:
    """Local storage writes a file under its root and removes it."""
    storage = LocalFileStorage(tmp_path)

    await storage.save(Path('avatars/user.png'), b'png-bytes')

    stored = tmp_path / 'avatars' / 'user.png'
    assert stored.read_bytes() == b'png-bytes'
    await storage.delete(Path('avatars/user.png'))
    assert not stored.exists()
    await storage.delete(Path('avatars/missing.png'))


async def test_local_storage_rejects_path_outside_root(tmp_path: Path) -> None:
    """A path that leaves the storage root is rejected."""
    storage = LocalFileStorage(tmp_path)

    with pytest.raises(BadRequestError, match='Invalid file path'):
        await storage.save(Path('../outside.txt'), b'data')

    assert list(tmp_path.iterdir()) == []


async def test_s3_storage_rejects_parent_path() -> None:
    """An S3 key with a parent segment is rejected before a client is created."""
    storage = S3FileStorage(bucket='bucket', access_key='key', secret_key='secret')

    with pytest.raises(BadRequestError, match='Invalid file path'):
        await storage.delete(Path('../secret'))


async def test_upload_avatar_rejects_missing_content_type(di_container: DIContainer) -> None:
    """A file without a content type is rejected."""
    await di_container.auth_service().register_user(
        CreateUserData(email='user@mail.ru', password='secret', nickname='nick'),
    )
    user = await InMemUserRepo().get_by_email('user@mail.ru')
    assert user is not None

    with pytest.raises(BadRequestError, match='Unsupported avatar file type'):
        await di_container.user_service().upload_avatar(user, b'png-bytes', None)
