from domain.exceptions import UserNicknameAlreadyTakenError
from domain.interfaces.repositories import UserRepo
from domain.models import User
from domain.services.base import BaseService
from .types import UpdateProfileData


class UserService(BaseService):
    """Profile changes for the user identified by the caller."""

    def __init__(self, users: UserRepo):
        self.user_repo: UserRepo = users

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
