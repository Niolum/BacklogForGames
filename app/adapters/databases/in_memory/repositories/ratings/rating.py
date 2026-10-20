from typing import ClassVar, override

from adapters.databases.in_memory.repositories.base import InMemBaseRepo
from domain.exceptions import RatingNotFoundError
from domain.interfaces.repositories import RatingRepo
from domain.models import Rating, RatingSummary


class InMemRatingRepo(InMemBaseRepo[Rating], RatingRepo):
    """In-memory user score repository."""

    DB: ClassVar[dict[int, Rating]] = {}

    @override
    async def create(self, rating: Rating) -> None:
        self._store(rating)

    @override
    async def get_by_user_and_game(self, user_id: int, game_id: int) -> Rating | None:
        return self._get(user_id=user_id, game_id=game_id)

    @override
    async def update(self, rating: Rating) -> None:
        if self._get(id=rating.id) is None:
            msg = f'Rating with id={rating.id} not found'
            raise RatingNotFoundError(msg)
        self._update(rating)

    @override
    async def get_summary(self, game_id: int) -> RatingSummary:
        scores = [rating.score for rating in self.DB.values() if rating.game_id == game_id]
        if not scores:
            return RatingSummary(users_score=None, ratings_count=0)
        return RatingSummary(users_score=sum(scores) / len(scores), ratings_count=len(scores))
