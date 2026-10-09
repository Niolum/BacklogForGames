from dependency_injector.wiring import Provide, inject

from domain.interfaces.uow import UnitOfWork
from domain.models import GamePage


@inject
async def get_games(
    *,
    genre_id: int | None = None,
    query: str | None = None,
    limit: int,
    offset: int,
    uow: UnitOfWork = Provide['uow'],
) -> GamePage:
    """Return one page of published games."""
    async with uow:
        return await uow.games.get_page(genre_id=genre_id, query=query, limit=limit, offset=offset)
