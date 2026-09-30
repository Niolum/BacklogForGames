from pathlib import Path
from uuid import UUID

from sqlalchemy.dialects import postgresql

from adapters.databases.sqlalchemy.types import PathType
from domain.models import User


def test_path_type_stores_text_and_loads_path() -> None:
    """PathType writes a path as text and reads it back as Path."""
    path_type = PathType()
    dialect = postgresql.dialect()
    stored = path_type.process_bind_param(Path('avatars/user.png'), dialect)
    loaded = path_type.process_result_value(stored, dialect)

    assert stored == 'avatars/user.png'
    assert loaded == Path('avatars/user.png')
    assert path_type.process_bind_param(None, dialect) is None
    assert path_type.process_result_value(None, dialect) is None


def test_user_avatar_is_path() -> None:
    """The user model keeps the avatar as Path."""
    user = User(
        id=1,
        uuid=UUID('0b6f1b0e-6c1a-4c3e-9b8a-1d2e3f4a5b6c'),
        nickname='nick',
        email='user@mail.ru',
        password='hash',
        avatar_url=Path('avatars/user.png'),
    )

    assert user.avatar_url == Path('avatars/user.png')
