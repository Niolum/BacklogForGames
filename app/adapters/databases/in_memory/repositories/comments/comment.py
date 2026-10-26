from typing import ClassVar, override
from uuid import UUID

from adapters.databases.in_memory.repositories.base import InMemBaseRepo
from adapters.databases.in_memory.repositories.users.user import InMemUserRepo
from domain.exceptions import CommentNotFoundError, UserNotFoundError
from domain.interfaces.repositories import CommentRepo
from domain.models import Comment, CommentAuthor, CommentItem, CommentPage


class InMemCommentRepo(InMemBaseRepo[Comment], CommentRepo):
    """In-memory comment repository."""

    DB: ClassVar[dict[int, Comment]] = {}

    @override
    async def create(self, comment: Comment) -> None:
        self._store(comment)

    @override
    async def get_by_uuid(self, comment_uuid: UUID) -> Comment | None:
        return self._get(uuid=comment_uuid)

    @override
    async def update(self, comment: Comment) -> None:
        if self._get(id=comment.id) is None:
            msg = f'Comment with id={comment.id} not found'
            raise CommentNotFoundError(msg)
        self._update(comment)

    @override
    async def delete(self, comment: Comment) -> None:
        if self._get(id=comment.id) is None:
            msg = f'Comment with id={comment.id} not found'
            raise CommentNotFoundError(msg)
        del self.DB[comment.id]

    @override
    async def get_page(self, *, game_id: int, limit: int, offset: int) -> CommentPage:
        matched = [comment for comment in self.DB.values() if comment.game_id == game_id]
        matched.sort(key=lambda comment: (comment.created_at, comment.id))
        items = [await self._item(comment) for comment in matched[offset : offset + limit]]
        return CommentPage(items=items, total=len(matched))

    async def _item(self, comment: Comment) -> CommentItem:
        user = await InMemUserRepo().get_by_id(comment.user_id)
        if user is None:
            msg = f'User with id={comment.user_id} not found'
            raise UserNotFoundError(msg)
        return CommentItem(
            uuid=comment.uuid,
            text=comment.text,
            created_at=comment.created_at,
            updated_at=comment.updated_at,
            author=CommentAuthor(uuid=user.uuid, nickname=user.nickname, avatar_url=user.avatar_url),
        )
