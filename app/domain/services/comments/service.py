from datetime import datetime
from uuid import uuid4

from config import settings
from domain.interfaces.repositories import CommentRepo
from domain.models import Comment, Game, User
from domain.services.base import BaseService


class CommentService(BaseService):
    """Stores a comment after the caller has already checked the game and the author."""

    def __init__(self, comments: CommentRepo):
        self.comment_repo: CommentRepo = comments

    async def create_comment(self, user: User, game: Game, text: str) -> Comment:
        """Store a new comment for this user and game."""
        comment = Comment(
            id=await self.comment_repo.get_next_id(),
            uuid=uuid4(),
            user_id=user.id,
            game_id=game.id,
            text=text,
        )
        await self.comment_repo.create(comment)
        return comment

    async def update_comment(self, comment: Comment, text: str) -> Comment:
        """Replace the text and the update time. The creation time stays."""
        updated = comment.model_copy(
            update={'text': text, 'updated_at': datetime.now(settings.default_timezone)},
        )
        await self.comment_repo.update(updated)
        return updated
