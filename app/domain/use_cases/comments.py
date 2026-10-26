from uuid import UUID

from dependency_injector.wiring import Provide, inject

from domain.exceptions import GameNotFoundError
from domain.interfaces.uow import UnitOfWork
from domain.models import CommentAuthor, CommentItem, User
from domain.services import CommentService, CreateCommentData


@inject
async def create_comment(
    user: User,
    game_uuid: UUID,
    data: CreateCommentData,
    uow: UnitOfWork = Provide['uow'],
    comment_service: CommentService = Provide['comment_service'],
) -> CommentItem:
    """Store a comment on a published game. List status is not checked."""
    async with uow:
        game = await uow.games.get_by_uuid_or_raise(game_uuid)
        if not game.is_published:
            msg = f'Game with uuid={game_uuid} not found'
            raise GameNotFoundError(msg)
        comment = await comment_service.create_comment(user, game, data.text)
        return CommentItem(
            uuid=comment.uuid,
            text=comment.text,
            created_at=comment.created_at,
            updated_at=comment.updated_at,
            author=CommentAuthor(uuid=user.uuid, nickname=user.nickname, avatar_url=user.avatar_url),
        )
