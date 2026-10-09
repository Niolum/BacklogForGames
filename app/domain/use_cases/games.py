from uuid import UUID

from dependency_injector.wiring import Provide, inject

from domain.exceptions import GameNotFoundError
from domain.interfaces.uow import UnitOfWork
from domain.models import Game, GamePage
from domain.services import GameChangeData, GameCreateData, GameService


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


@inject
async def get_game_by_uuid(
    game_uuid: UUID,
    uow: UnitOfWork = Provide['uow'],
) -> Game:
    """Load a published game by the public uuid."""
    async with uow:
        game = await uow.games.get_by_uuid_or_raise(game_uuid)
        if not game.is_published:
            msg = f'Game with uuid={game_uuid} not found'
            raise GameNotFoundError(msg)
        return game


@inject
async def create_game(
    data: GameCreateData,
    uow: UnitOfWork = Provide['uow'],
    game_service: GameService = Provide['game_service'],
) -> Game:
    """Create a game from the admin panel."""
    async with uow:
        return await game_service.create_game(data)


@inject
async def update_game(
    game_id: int,
    data: GameChangeData,
    uow: UnitOfWork = Provide['uow'],
    game_service: GameService = Provide['game_service'],
) -> Game:
    """Change a game from the admin panel."""
    async with uow:
        return await game_service.update_game(game_id, data)
