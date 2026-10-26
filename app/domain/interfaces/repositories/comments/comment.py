from abc import abstractmethod
from uuid import UUID

from domain.exceptions import CommentNotFoundError
from domain.interfaces.repositories.base import BaseRepo
from domain.models import Comment, CommentPage


class CommentRepo(BaseRepo):
    """Comment repository."""

    @abstractmethod
    async def get_next_id(self) -> int:
        """Get next ID."""

    @abstractmethod
    async def create(self, comment: Comment) -> None:
        """Create a comment."""

    @abstractmethod
    async def get_by_uuid(self, comment_uuid: UUID) -> Comment | None:
        """Get a comment by the public uuid."""

    async def get_by_uuid_or_raise(self, comment_uuid: UUID) -> Comment:
        """Get a comment by the public uuid or raise exception."""
        comment = await self.get_by_uuid(comment_uuid)
        if comment is None:
            msg = f'Comment with uuid={comment_uuid} not found'
            raise CommentNotFoundError(msg)
        return comment

    @abstractmethod
    async def update(self, comment: Comment) -> None:
        """Update a comment."""

    @abstractmethod
    async def delete(self, comment: Comment) -> None:
        """Delete a comment."""

    @abstractmethod
    async def get_page(self, *, game_id: int, limit: int, offset: int) -> CommentPage:
        """Return one page of a game's comments, ordered by creation time."""
