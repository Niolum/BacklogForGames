from datetime import datetime
from uuid import uuid4

from config import settings
from domain.exceptions import GenreNotFoundError
from domain.interfaces.repositories import GameRepo, GenreRepo
from domain.models import Game, Genre
from domain.services.base import BaseService
from .types import GameChangeData, GameCreateData


class GameService(BaseService):
    """Create and edit catalog games."""

    def __init__(self, games: GameRepo, genres: GenreRepo):
        self.game_repo: GameRepo = games
        self.genre_repo: GenreRepo = genres

    async def create_game(self, data: GameCreateData) -> Game:
        """Create a game and store its genres."""
        game = Game(
            id=await self.game_repo.get_next_id(),
            uuid=uuid4(),
            title=data.title,
            release_date=data.release_date,
            description=data.description,
            metacritic=data.metacritic,
            developer=data.developer,
            publisher=data.publisher,
            is_published=data.is_published,
            genres=await self._genres(data.genres),
        )
        await self.game_repo.create(game)
        return game

    async def update_game(self, game_id: int, data: GameChangeData) -> Game:
        """Change the editable fields. External identity and the cover stay as they are."""
        game = await self.game_repo.get_by_id_or_raise(game_id)
        updated = game.model_copy(
            update={
                'title': data.title,
                'release_date': data.release_date,
                'description': data.description,
                'metacritic': data.metacritic,
                'developer': data.developer,
                'publisher': data.publisher,
                'is_published': data.is_published,
                'genres': await self._genres(data.genres),
                'updated_at': datetime.now(settings.default_timezone),
            },
        )
        await self.game_repo.update(updated)
        return updated

    async def _genres(self, genre_ids: list[int]) -> list[Genre]:
        unique: dict[int, Genre] = {}
        for genre_id in genre_ids:
            if genre_id in unique:
                continue
            genre = await self.genre_repo.get_by_id(genre_id)
            if genre is None:
                msg = f'Genre with id={genre_id} not found'
                raise GenreNotFoundError(msg)
            unique[genre_id] = genre
        return [unique[genre_id] for genre_id in sorted(unique)]
