from typing import override

from sqlalchemy import select, text

from adapters.databases.sqlalchemy.models import GenreORM
from adapters.databases.sqlalchemy.repositories.base import SQLABaseRepo
from domain.exceptions import GenreNotFoundError
from domain.interfaces.repositories import GenreRepo
from domain.models import Genre


class SQLAGenreRepo(SQLABaseRepo, GenreRepo):
    """Реализация репозитория жанров на SQLAlchemy."""

    @override
    async def get_next_id(self) -> int:
        res = await self.session.execute(text("select nextval('genres_id_seq')"))
        return res.scalar_one()

    @override
    async def create(self, genre: Genre) -> None:
        genre_orm = GenreORM(**genre.model_dump())
        self.session.add(genre_orm)
        await self.session.flush()
        await self.session.refresh(genre_orm)

    @override
    async def get_by_id(self, genre_id: int) -> Genre | None:
        return await self._get_genre(GenreORM.id == genre_id)

    @override
    async def get_by_name(self, name: str) -> Genre | None:
        return await self._get_genre(GenreORM.name == name)

    @override
    async def get_all(self) -> list[Genre]:
        result = await self.session.execute(select(GenreORM).order_by(GenreORM.id))
        return [genre_orm.to_domain() for genre_orm in result.scalars()]

    @override
    async def update(self, genre: Genre) -> None:
        genre_orm = await self.session.get(GenreORM, genre.id)
        if genre_orm is None:
            msg = f'Genre with id={genre.id} not found'
            raise GenreNotFoundError(msg)
        for field, value in genre.model_dump().items():
            setattr(genre_orm, field, value)
        await self.session.flush()

    @override
    async def delete(self, genre: Genre) -> None:
        genre_orm = await self.session.get(GenreORM, genre.id)
        if genre_orm is None:
            msg = f'Genre with id={genre.id} not found'
            raise GenreNotFoundError(msg)
        await self.session.delete(genre_orm)
        await self.session.flush()

    async def _get_genre(self, *criteria) -> Genre | None:
        """Return one genre matching the criteria."""
        result = await self.session.execute(select(GenreORM).where(*criteria))
        genre_orm = result.scalar_one_or_none()
        if genre_orm is None:
            return None
        return genre_orm.to_domain()
