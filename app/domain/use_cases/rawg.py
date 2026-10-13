from dependency_injector.wiring import Provide, inject

from domain.interfaces.uow import UnitOfWork
from domain.services import RawgService


@inject
async def import_catalog(
    limit: int,
    uow: UnitOfWork = Provide['uow'],
    rawg_service: RawgService = Provide['rawg_service'],
) -> None:
    """Import genres and games from RAWG up to the given game limit."""
    async with uow:
        await rawg_service.import_games(limit)
