from typing import override
from uuid import UUID

from sqlalchemy import func, select, text
from sqlalchemy.sql import Select

from adapters.databases.sqlalchemy.models import GameORM, GenreORM
from adapters.databases.sqlalchemy.repositories.base import SQLABaseRepo
from domain.exceptions import GameNotFoundError, GenreNotFoundError
from domain.interfaces.repositories import GameRepo
from domain.models import Game, GamePage, Genre


class SQLAGameRepo(SQLABaseRepo, GameRepo):
    """Implementing a game repository using SQLAlchemy."""

    @override
    async def get_next_id(self) -> int:
        res = await self.session.execute(text("select nextval('games_id_seq')"))
        return res.scalar_one()

    @override
    async def create(self, game: Game) -> None:
        game_orm = GameORM.from_model(game)
        game_orm.genres = await self._genres(game.genres)
        self.session.add(game_orm)
        await self.session.flush()

    @override
    async def get_by_id(self, game_id: int) -> Game | None:
        return await self._get_game(GameORM.id == game_id)

    @override
    async def get_by_uuid(self, game_uuid: UUID) -> Game | None:
        return await self._get_game(GameORM.uuid == game_uuid)

    @override
    async def update(self, game: Game) -> None:
        game_orm: GameORM | None = await self.session.get(GameORM, game.id)
        if game_orm is None:
            msg = f'Game with id={game.id} not found'
            raise GameNotFoundError(msg)
        for field, value in game.model_dump(exclude={'genres'}).items():
            setattr(game_orm, field, value)
        game_orm.genres = await self._genres(game.genres)
        await self.session.flush()

    @override
    async def get_page(
        self,
        *,
        genre_id: int | None = None,
        query: str | None = None,
        limit: int,
        offset: int,
    ) -> GamePage:
        filtered = self._filtered(genre_id, query)
        total = await self.session.scalar(select(func.count()).select_from(filtered.subquery()))
        result = await self.session.execute(
            filtered.order_by(func.lower(GameORM.title)).limit(limit).offset(offset),
        )
        return GamePage(items=[await game_orm.to_domain() for game_orm in result.scalars()], total=total or 0)

    async def _genres(self, genres: list[Genre]) -> list[GenreORM]:
        unique: dict[int, GenreORM] = {}
        for genre in genres:
            if genre.id in unique:
                continue
            genre_orm = await self.session.get(GenreORM, genre.id)
            if genre_orm is None:
                msg = f'Genre with id={genre.id} not found'
                raise GenreNotFoundError(msg)
            unique[genre.id] = genre_orm
        return [unique[genre_id] for genre_id in sorted(unique)]

    async def _get_game(self, *criteria) -> Game | None:
        result = await self.session.execute(select(GameORM).where(*criteria))
        game_orm = result.scalar_one_or_none()
        if game_orm is None:
            return None
        return await game_orm.to_domain()

    def _filtered(self, genre_id: int | None, query: str | None) -> Select[GameORM]:
        stmt = select(GameORM).where(GameORM.is_published.is_(True))
        if genre_id is not None:
            stmt = stmt.where(GameORM.genres.any(GenreORM.id == genre_id))
        if query:
            stmt = stmt.where(GameORM.title.ilike(self._title_pattern(query), escape='\\'))
        return stmt

    def _title_pattern(self, query: str) -> str:
        escaped = query.replace('\\', '\\\\').replace('%', '\\%').replace('_', '\\_')
        return f'%{escaped}%'
