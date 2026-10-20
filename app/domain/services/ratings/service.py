from datetime import datetime

from config import settings
from domain.interfaces.repositories import RatingRepo
from domain.models import Game, Rating, User
from domain.services.base import BaseService


class RatingService(BaseService):
    """Stores a score after the caller has already checked the game and the list."""

    def __init__(self, ratings: RatingRepo):
        self.rating_repo: RatingRepo = ratings

    async def create_rating(self, user: User, game: Game, score: int) -> Rating:
        """Store a new score for this user and game."""
        rating = Rating(
            id=await self.rating_repo.get_next_id(),
            user_id=user.id,
            game_id=game.id,
            score=score,
        )
        await self.rating_repo.create(rating)
        return rating

    async def update_rating(self, rating: Rating, score: int) -> Rating:
        """Replace the score and the update time. The creation time stays."""
        updated = rating.model_copy(
            update={'score': score, 'updated_at': datetime.now(settings.default_timezone)},
        )
        await self.rating_repo.update(updated)
        return updated
