from uuid import UUID

from fastapi import APIRouter, Query, status

from domain.constants import DEFAULT_LIMIT
from domain.services import CreateCommentData, SetRatingData
from domain.use_cases import create_comment, get_game_card, get_game_comments, get_games, set_rating
from entrypoints.fastapi.dependencies import CurrentUser, OptionalCurrentUser
from entrypoints.fastapi.schemas.request import CreateCommentRequestSchema, SetRatingRequestSchema
from entrypoints.fastapi.schemas.response import (
    CommentPageResponseSchema,
    CommentResponseSchema,
    GameCardResponseSchema,
    GamePageResponseSchema,
    GameResponseSchema,
    RatingResponseSchema,
)


game_router = APIRouter(prefix='/games', tags=['Game'])


@game_router.get('', response_model=GamePageResponseSchema)
async def list_games_handler(
    genre_id: int | None = None,
    q: str | None = None,
    limit: int = Query(default=DEFAULT_LIMIT, ge=1),
    offset: int = Query(default=0, ge=0),
) -> GamePageResponseSchema:
    """Return one page of published games. No token is required."""
    page = await get_games(genre_id=genre_id, query=q, limit=limit, offset=offset)
    return GamePageResponseSchema(
        items=[GameResponseSchema.model_validate(game.model_dump()) for game in page.items],
        total=page.total,
    )


@game_router.get('/{game_uuid}/comments', response_model=CommentPageResponseSchema)
async def list_comments_handler(
    game_uuid: UUID,
    limit: int = Query(default=DEFAULT_LIMIT, ge=1),
    offset: int = Query(default=0, ge=0),
) -> CommentPageResponseSchema:
    """Return one page of comments on a published game. No token is required."""
    page = await get_game_comments(game_uuid, limit=limit, offset=offset)
    return CommentPageResponseSchema(
        items=[CommentResponseSchema.model_validate(item.model_dump()) for item in page.items],
        total=page.total,
    )


@game_router.post(
    '/{game_uuid}/comments',
    response_model=CommentResponseSchema,
    status_code=status.HTTP_201_CREATED,
)
async def create_comment_handler(
    current_user: CurrentUser,
    game_uuid: UUID,
    request_data: CreateCommentRequestSchema,
) -> CommentResponseSchema:
    """Store a comment on a published game. List status is not checked."""
    data = CreateCommentData.model_validate(request_data.model_dump())
    comment = await create_comment(current_user, game_uuid, data)
    return CommentResponseSchema.model_validate(comment.model_dump())


@game_router.put('/{game_uuid}/rating', response_model=RatingResponseSchema)
async def set_rating_handler(
    current_user: CurrentUser,
    game_uuid: UUID,
    request_data: SetRatingRequestSchema,
) -> RatingResponseSchema:
    """Save the current user's score for a completed game."""
    data = SetRatingData.model_validate(request_data.model_dump())
    rating = await set_rating(current_user, game_uuid, data)
    return RatingResponseSchema(score=rating.score)


@game_router.get('/{game_uuid}', response_model=GameCardResponseSchema)
async def game_handler(game_uuid: UUID, current_user: OptionalCurrentUser) -> GameCardResponseSchema:
    """Return one published game. An unknown uuid and a hidden game respond with 404."""
    card = await get_game_card(game_uuid, current_user)
    return GameCardResponseSchema.model_validate(
        card.game.model_dump()
        | {
            'users_score': card.summary.users_score,
            'ratings_count': card.summary.ratings_count,
            'user_score': card.user_score,
        },
    )
