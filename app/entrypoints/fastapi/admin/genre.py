from typing import Any, override

from sqladmin import ModelView
from starlette.requests import Request

from adapters.databases.sqlalchemy.models import GenreORM
from domain.services import GenreChangeData, GenreCreateData
from domain.use_cases import create_genre, delete_genre, update_genre


class GenreAdmin(ModelView, model=GenreORM):
    """Genre screen of the admin panel."""

    name = 'Genre'
    name_plural = 'Genres'
    column_list = [GenreORM.id, GenreORM.name, GenreORM.description]
    form_columns = [GenreORM.name, GenreORM.description]

    @override
    async def insert_model(self, request: Request, data: dict) -> GenreORM:
        """Create a genre through the domain service."""
        genre = await create_genre(GenreCreateData.model_validate(data))
        return GenreORM.from_model(genre)

    @override
    async def update_model(self, request: Request, pk: str, data: dict) -> GenreORM:
        """Change the genre name and description through the domain service."""
        genre = await update_genre(int(pk), GenreChangeData.model_validate(data))
        return GenreORM.from_model(genre)

    @override
    async def delete_model(self, request: Request, pk: Any) -> None:
        """Delete a genre through the domain service."""
        await delete_genre(int(pk))


GenreAdmin.identity = 'genre'
