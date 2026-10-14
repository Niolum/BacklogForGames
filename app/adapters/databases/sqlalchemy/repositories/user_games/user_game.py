from typing import override

from sqlalchemy import func, select, text
from sqlalchemy.sql import Select

from adapters.databases.sqlalchemy.models import GameORM, UserGameORM
from adapters.databases.sqlalchemy.repositories.base import SQLABaseRepo
from domain.exceptions import UserGameNotFoundError
from domain.interfaces.repositories import UserGameRepo
from domain.models import UserGame, UserGamePage, UserGameStatus


class SQLAUserGameRepo(SQLABaseRepo, UserGameRepo):
    """Implementing a user list repository using SQLAlchemy."""

    @override
    async def get_next_id(self) -> int:
        res = await self.session.execute(text("select nextval('user_games_id_seq')"))
        return res.scalar_one()

    @override
    async def create(self, user_game: UserGame) -> None:
        self.session.add(UserGameORM.from_model(user_game))
        await self.session.flush()

    @override
    async def get_by_user_and_game(self, user_id: int, game_id: int) -> UserGame | None:
        result = await self.session.execute(
            select(UserGameORM).where(UserGameORM.user_id == user_id, UserGameORM.game_id == game_id),
        )
        user_game_orm = result.scalar_one_or_none()
        if user_game_orm is None:
            return None
        return user_game_orm.to_domain()

    @override
    async def update(self, user_game: UserGame) -> None:
        user_game_orm = await self.session.get(UserGameORM, user_game.id)
        if user_game_orm is None:
            msg = f'User game with id={user_game.id} not found'
            raise UserGameNotFoundError(msg)
        for field, value in user_game.model_dump().items():
            setattr(user_game_orm, field, value)
        await self.session.flush()

    @override
    async def delete(self, user_game: UserGame) -> None:
        user_game_orm = await self.session.get(UserGameORM, user_game.id)
        if user_game_orm is None:
            msg = f'User game with id={user_game.id} not found'
            raise UserGameNotFoundError(msg)
        await self.session.delete(user_game_orm)
        await self.session.flush()

    @override
    async def get_page(
        self,
        *,
        user_id: int,
        status: UserGameStatus,
        limit: int,
        offset: int,
    ) -> UserGamePage:
        filtered = self._filtered(user_id, status)
        total = await self.session.scalar(select(func.count()).select_from(filtered.subquery()))
        result = await self.session.execute(
            filtered.order_by(func.lower(GameORM.title), GameORM.id).limit(limit).offset(offset),
        )
        items = [await game_orm.to_domain() for game_orm in result.scalars()]
        return UserGamePage(items=items, total=total or 0)

    def _filtered(self, user_id: int, status: UserGameStatus) -> Select[GameORM]:
        return (
            select(GameORM)
            .join(UserGameORM, UserGameORM.game_id == GameORM.id)
            .where(
                UserGameORM.user_id == user_id,
                UserGameORM.status == status,
            )
        )
