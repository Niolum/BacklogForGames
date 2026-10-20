from uuid import UUID

from fastapi import APIRouter, Query

from domain.constants import DEFAULT_LIMIT
from domain.services import SetRatingData
from domain.use_cases import get_game_by_uuid, get_games, set_rating
from entrypoints.fastapi.dependencies import CurrentUser
from entrypoints.fastapi.schemas.request import SetRatingRequestSchema
from entrypoints.fastapi.schemas.response import (
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
async def game_handler(game_uuid: UUID) -> GameCardResponseSchema:
    """Return one published game. An unknown uuid and a hidden game respond with 404."""
    game = await get_game_by_uuid(game_uuid)
    return GameCardResponseSchema.model_validate(game.model_dump())
