from dependency_injector.wiring import Provide, inject

from domain.interfaces.uow import UnitOfWork
from domain.models import Genre


@inject
async def get_genres(
    uow: UnitOfWork = Provide['uow'],
) -> list[Genre]:
    """Return every genre ordered by id."""
    async with uow:
        return await uow.genres.get_all()


@inject
async def get_genre_by_id(
    genre_id: int,
    uow: UnitOfWork = Provide['uow'],
) -> Genre:
    """Load a genre by id."""
    async with uow:
        return await uow.genres.get_by_id_or_raise(genre_id)
