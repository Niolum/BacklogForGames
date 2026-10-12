from datetime import datetime
from uuid import uuid4

from config import settings, storage_settings
from domain.constants import COVER_EXTENSIONS, COVER_MAX_BYTES
from domain.exceptions import GenreNotFoundError, UploadFileTypeError, UploadGameCoverError
from domain.interfaces.repositories import GameRepo, GenreRepo
from domain.interfaces.storage import FileStorage
from domain.models import Game, Genre
from domain.services.base import BaseService
from .types import GameChangeData, GameCoverData, GameCreateData


class GameService(BaseService):
    """Create and edit catalog games."""

    def __init__(self, games: GameRepo, genres: GenreRepo, file_storage: FileStorage):
        self.game_repo: GameRepo = games
        self.genre_repo: GenreRepo = genres
        self.file_storage: FileStorage = file_storage

    async def create_game(
        self,
        data: GameCreateData,
        cover: GameCoverData | None = None,
    ) -> Game:
        """Create a game and store its genres. A cover file is saved with the game."""
        if cover is not None:
            self._ensure_cover(cover)
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
        if cover is None:
            return game
        return await self._store_cover(game, cover)

    async def update_game(
        self,
        game_id: int,
        data: GameChangeData,
        cover: GameCoverData | None = None,
    ) -> Game:
        """Change the editable fields. External identity stays. A new cover replaces the old file."""
        if cover is not None:
            self._ensure_cover(cover)
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
        if cover is None:
            return updated
        return await self._store_cover(updated, cover)

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

    async def _store_cover(self, game: Game, cover: GameCoverData) -> Game:
        extension = self._cover_extension(cover)
        path = storage_settings.base_game_cover_path / f'{game.uuid}{extension}'
        await self.file_storage.save(path, cover.content)
        previous = game.cover_url
        updated = game.model_copy(
            update={'cover_url': path, 'updated_at': datetime.now(settings.default_timezone)},
        )
        await self.game_repo.update(updated)
        if previous is not None and previous != path:
            await self.file_storage.delete(previous)
        return updated

    def _ensure_cover(self, cover: GameCoverData) -> None:
        self._cover_extension(cover)
        if not cover.content:
            msg = 'Cover file is empty'
            raise UploadGameCoverError(msg)
        if len(cover.content) > COVER_MAX_BYTES:
            msg = 'Cover file is too large'
            raise UploadGameCoverError(msg)

    def _cover_extension(self, cover: GameCoverData) -> str:
        """Map a supported image content type to a file extension."""
        if not cover.content_type:
            msg = 'Unsupported cover file type'
            raise UploadFileTypeError(msg)
        media_type = cover.content_type.split(';', maxsplit=1)[0].strip().lower()
        extension = COVER_EXTENSIONS.get(media_type)
        if extension is None:
            msg = 'Unsupported cover file type'
            raise UploadFileTypeError(msg)
        return extension
