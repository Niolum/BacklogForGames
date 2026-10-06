from dependency_injector.wiring import Provide, inject

from domain.interfaces.uow import UnitOfWork
from domain.models import Genre
from domain.services import GenreChangeData, GenreCreateData, GenreService


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


@inject
async def create_genre(
    data: GenreCreateData,
    uow: UnitOfWork = Provide['uow'],
    genre_service: GenreService = Provide['genre_service'],
) -> Genre:
    """Create a genre from the admin panel."""
    async with uow:
        return await genre_service.create_genre(data)


@inject
async def update_genre(
    genre_id: int,
    data: GenreChangeData,
    uow: UnitOfWork = Provide['uow'],
    genre_service: GenreService = Provide['genre_service'],
) -> Genre:
    """Change a genre name and description from the admin panel."""
    async with uow:
        return await genre_service.update_genre(genre_id, data)


@inject
async def delete_genre(
    genre_id: int,
    uow: UnitOfWork = Provide['uow'],
    genre_service: GenreService = Provide['genre_service'],
) -> None:
    """Delete a genre from the admin panel."""
    async with uow:
        await genre_service.delete_genre(genre_id)
