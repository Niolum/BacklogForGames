from config import storage_settings
from domain.constants import AVATAR_EXTENSIONS, AVATAR_MAX_BYTES
from domain.exceptions import UploadFileTypeError, UploadUserAvatarError, UserNicknameAlreadyTakenError
from domain.interfaces.repositories import UserRepo
from domain.interfaces.storage import FileStorage
from domain.models import User
from domain.services.base import BaseService
from .types import UpdateProfileData


class UserService(BaseService):
    """Profile changes for the user identified by the caller."""

    def __init__(self, users: UserRepo, file_storage: FileStorage):
        self.user_repo: UserRepo = users
        self.file_storage: FileStorage = file_storage

    async def update_profile(self, user: User, data: UpdateProfileData) -> User:
        """Update nickname, date of birth and about. A taken nickname is a conflict."""
        changes = data.model_dump(exclude_unset=True)
        nickname = changes.get('nickname')
        if nickname is not None:
            existing = await self.user_repo.get_by_nickname(nickname)
            if existing is not None and existing.id != user.id:
                msg = f'User with nickname={nickname} already exists'
                raise UserNicknameAlreadyTakenError(msg)

        updated = user.model_copy(update=changes)
        await self.user_repo.update(updated)
        return updated

    async def upload_avatar(self, user: User, content: bytes, content_type: str | None) -> User:
        """Store an avatar for this user and return the updated profile."""
        extension = self._avatar_extension(content_type)
        if not content:
            msg = 'Avatar file is empty'
            raise UploadUserAvatarError(msg)
        if len(content) > AVATAR_MAX_BYTES:
            msg = 'Avatar file is too large'
            raise UploadUserAvatarError(msg)

        path = storage_settings.base_user_avatar_path / f'{user.uuid}{extension}'
        await self.file_storage.save(path, content)
        previous = user.avatar_url
        updated = user.model_copy(update={'avatar_url': path})
        await self.user_repo.update(updated)
        if previous is not None and previous != path:
            await self.file_storage.delete(previous)
        return updated

    async def delete_avatar(self, user: User) -> None:
        """Remove the avatar of this user."""
        if user.avatar_url is None:
            return
        await self.file_storage.delete(user.avatar_url)
        await self.user_repo.update(user.model_copy(update={'avatar_url': None}))

    def _avatar_extension(self, content_type: str | None) -> str:
        """Map a supported image content type to a file extension."""
        if not content_type:
            msg = 'Unsupported avatar file type'
            raise UploadFileTypeError(msg)
        media_type = content_type.split(';', maxsplit=1)[0].strip().lower()
        extension = AVATAR_EXTENSIONS.get(media_type)
        if extension is None:
            msg = 'Unsupported avatar file type'
            raise UploadFileTypeError(msg)
        return extension
