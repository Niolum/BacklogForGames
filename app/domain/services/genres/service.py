from domain.exceptions import GenreHasGamesError, GenreNameAlreadyTakenError
from domain.interfaces.repositories import GenreRepo
from domain.models import Genre
from domain.services.base import BaseService
from .types import GenreChangeData, GenreCreateData


class GenreService(BaseService):
    """Create, rename and delete genres."""

    def __init__(self, genres: GenreRepo):
        self.genre_repo: GenreRepo = genres

    async def create_genre(self, data: GenreCreateData) -> Genre:
        """Create a genre. A taken name is a conflict."""
        await self._ensure_name_is_free(data.name)
        genre = Genre(
            id=await self.genre_repo.get_next_id(),
            name=data.name,
            description=data.description,
        )
        await self.genre_repo.create(genre)
        return genre

    async def update_genre(self, genre_id: int, data: GenreChangeData) -> Genre:
        """Change the name and description. External fields stay as they are."""
        genre = await self.genre_repo.get_by_id_or_raise(genre_id)
        await self._ensure_name_is_free(data.name, genre_id=genre.id)
        updated = genre.model_copy(update={'name': data.name, 'description': data.description})
        await self.genre_repo.update(updated)
        return updated

    async def delete_genre(self, genre_id: int) -> None:
        """Delete a genre that no game references."""
        genre = await self.genre_repo.get_by_id_or_raise(genre_id)
        if await self.genre_repo.has_games(genre.id):
            msg = f'Genre with id={genre.id} cannot be deleted because games use it'
            raise GenreHasGamesError(msg)
        await self.genre_repo.delete(genre)

    async def _ensure_name_is_free(self, name: str, genre_id: int | None = None) -> None:
        existing = await self.genre_repo.get_by_name(name)
        if existing is not None and existing.id != genre_id:
            msg = f'Genre with name={name} already exists'
            raise GenreNameAlreadyTakenError(msg)
