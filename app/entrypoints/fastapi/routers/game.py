from fastapi import APIRouter, Query

from domain.use_cases import get_games
from entrypoints.fastapi.schemas.response import GamePageResponseSchema, GameResponseSchema


game_router = APIRouter(prefix='/games', tags=['Game'])

_DEFAULT_LIMIT = 20


@game_router.get('', response_model=GamePageResponseSchema)
async def list_games_handler(
    genre_id: int | None = None,
    q: str | None = None,
    limit: int = Query(default=_DEFAULT_LIMIT, ge=1),
    offset: int = Query(default=0, ge=0),
) -> GamePageResponseSchema:
    """Return one page of published games. No token is required."""
    page = await get_games(genre_id=genre_id, query=q, limit=limit, offset=offset)
    return GamePageResponseSchema(
        items=[GameResponseSchema.model_validate(game.model_dump()) for game in page.items],
        total=page.total,
    )
