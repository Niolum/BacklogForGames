from uuid import uuid4

from domain.interfaces.repositories import CommentRepo
from domain.models import Comment, Game, User
from domain.services.base import BaseService


class CommentService(BaseService):
    """Stores a comment after the caller has already checked the game."""

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
