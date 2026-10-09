from uuid import UUID

from fastapi import APIRouter, Query

from domain.constants import DEFAULT_LIMIT
from domain.use_cases import get_game_by_uuid, get_games
from entrypoints.fastapi.schemas.response import GameCardResponseSchema, GamePageResponseSchema, GameResponseSchema


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


@game_router.get('/{game_uuid}', response_model=GameCardResponseSchema)
async def game_handler(game_uuid: UUID) -> GameCardResponseSchema:
    """Return one published game. An unknown uuid and a hidden game respond with 404."""
    game = await get_game_by_uuid(game_uuid)
    return GameCardResponseSchema.model_validate(game.model_dump())
