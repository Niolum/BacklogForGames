from decimal import Decimal
from typing import override

from sqlalchemy import func, select, text

from adapters.databases.sqlalchemy.models import RatingORM
from adapters.databases.sqlalchemy.repositories.base import SQLABaseRepo
from domain.exceptions import RatingNotFoundError
from domain.interfaces.repositories import RatingRepo
from domain.models import Rating, RatingSummary


class SQLARatingRepo(SQLABaseRepo, RatingRepo):
    """Implementing a user score repository using SQLAlchemy."""

    @override
    async def get_next_id(self) -> int:
        res = await self.session.execute(text("select nextval('ratings_id_seq')"))
        return res.scalar_one()

    @override
    async def create(self, rating: Rating) -> None:
        self.session.add(RatingORM.from_model(rating))
        await self.session.flush()

    @override
    async def get_by_user_and_game(self, user_id: int, game_id: int) -> Rating | None:
        result = await self.session.execute(
            select(RatingORM).where(RatingORM.user_id == user_id, RatingORM.game_id == game_id),
        )
        rating_orm = result.scalar_one_or_none()
        if rating_orm is None:
            return None
        return rating_orm.to_domain()

    @override
    async def update(self, rating: Rating) -> None:
        rating_orm = await self.session.get(RatingORM, rating.id)
        if rating_orm is None:
            msg = f'Rating with id={rating.id} not found'
            raise RatingNotFoundError(msg)
        for field, value in rating.model_dump().items():
            setattr(rating_orm, field, value)
        await self.session.flush()

    @override
    async def get_summary(self, game_id: int) -> RatingSummary:
        result = await self.session.execute(
            select(func.avg(RatingORM.score), func.count()).where(RatingORM.game_id == game_id),
        )
        average, total = result.one()
        if isinstance(average, Decimal | float | int):
            users_score = float(average)
        elif average is None:
            users_score = None
        else:
            msg = 'Average score has an unexpected type'
            raise TypeError(msg)
        if not isinstance(total, int):
            msg = 'Rating count has an unexpected type'
            raise TypeError(msg)
        return RatingSummary(users_score=users_score, ratings_count=total)
