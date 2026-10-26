from uuid import UUID

from dependency_injector.wiring import Provide, inject

from domain.exceptions import CommentNotFoundError, GameNotFoundError
from domain.interfaces.uow import UnitOfWork
from domain.models import Comment, CommentAuthor, CommentItem, CommentPage, Game, User
from domain.services import CommentService, CreateCommentData, UpdateCommentData


@inject
async def get_game_comments(
    game_uuid: UUID,
    *,
    limit: int,
    offset: int,
    uow: UnitOfWork = Provide['uow'],
) -> CommentPage:
    """Return one page of comments on a published game."""
    async with uow:
        game = await _published_game(game_uuid, uow)
        return await uow.comments.get_page(game_id=game.id, limit=limit, offset=offset)


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
        game = await _published_game(game_uuid, uow)
        comment = await comment_service.create_comment(user, game, data.text)
        return _comment_item(comment, user)


@inject
async def update_comment(
    user: User,
    comment_uuid: UUID,
    data: UpdateCommentData,
    uow: UnitOfWork = Provide['uow'],
    comment_service: CommentService = Provide['comment_service'],
) -> CommentItem:
    """Replace the current user's comment text. Another user's comment stays."""
    async with uow:
        comment = await uow.comments.get_by_uuid_or_raise(comment_uuid)
        if comment.user_id != user.id:
            msg = f'Comment with uuid={comment_uuid} not found'
            raise CommentNotFoundError(msg)
        updated = await comment_service.update_comment(comment, data.text)
        return _comment_item(updated, user)


def _comment_item(comment: Comment, user: User) -> CommentItem:
    """Build the public comment from the stored row and its author."""
    return CommentItem(
        uuid=comment.uuid,
        text=comment.text,
        created_at=comment.created_at,
        updated_at=comment.updated_at,
        author=CommentAuthor(uuid=user.uuid, nickname=user.nickname, avatar_url=user.avatar_url),
    )


async def _published_game(game_uuid: UUID, uow: UnitOfWork) -> Game:
    """Load a published game or raise the catalog not-found error."""
    game = await uow.games.get_by_uuid_or_raise(game_uuid)
    if not game.is_published:
        msg = f'Game with uuid={game_uuid} not found'
        raise GameNotFoundError(msg)
    return game
