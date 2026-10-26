from uuid import UUID

from dependency_injector.wiring import Provide, inject

from domain.exceptions import GameNotFoundError
from domain.interfaces.uow import UnitOfWork
from domain.models import Game, GameCard, GamePage, User, UserGameStatus
from domain.services import GameChangeData, GameCoverData, GameCreateData, GameService


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
        return await _published_game(game_uuid, uow)


@inject
async def get_game_card(
    game_uuid: UUID,
    user: User | None = None,
    uow: UnitOfWork = Provide['uow'],
) -> GameCard:
    """Load a published game, its scores, and the caller's list status."""
    async with uow:
        game = await _published_game(game_uuid, uow)
        summary = await uow.ratings.get_summary(game.id)
        user_score = None
        list_status: UserGameStatus | None = None
        if user is not None:
            rating = await uow.ratings.get_by_user_and_game(user.id, game.id)
            if rating is not None:
                user_score = rating.score
            user_game = await uow.user_games.get_by_user_and_game(user.id, game.id)
            if user_game is not None:
                list_status = user_game.status
        return GameCard(game=game, summary=summary, user_score=user_score, list_status=list_status)


async def _published_game(game_uuid: UUID, uow: UnitOfWork) -> Game:
    """Load a published game or raise the catalog not-found error."""
    game = await uow.games.get_by_uuid_or_raise(game_uuid)
    if not game.is_published:
        msg = f'Game with uuid={game_uuid} not found'
        raise GameNotFoundError(msg)
    return game


@inject
async def create_game(
    data: GameCreateData,
    cover: GameCoverData | None = None,
    uow: UnitOfWork = Provide['uow'],
    game_service: GameService = Provide['game_service'],
) -> Game:
    """Create a game from the admin panel."""
    async with uow:
        return await game_service.create_game(data, cover=cover)


@inject
async def update_game(
    game_id: int,
    data: GameChangeData,
    cover: GameCoverData | None = None,
    uow: UnitOfWork = Provide['uow'],
    game_service: GameService = Provide['game_service'],
) -> Game:
    """Change a game from the admin panel."""
    async with uow:
        return await game_service.update_game(game_id, data, cover=cover)
