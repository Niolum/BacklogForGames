from datetime import datetime
from http import HTTPMethod
from uuid import uuid4

from config import rawg_settings, settings
from domain.constants import RAWG_MAX_PAGE_SIZE, RAWG_SOURCE
from domain.exceptions import BadRequestError, GenreNameAlreadyTakenError
from domain.interfaces.http_fetcher import HttpAPIFetcher
from domain.interfaces.repositories import GameRepo, GenreRepo
from domain.logger import logger
from domain.models import Game, Genre
from domain.services.base import BaseService
from .types import RawgGameCard, RawgGamesPage, RawgGenreCard, RawgListedGame


class RawgService(BaseService):
    """Reads RAWG and imports a limited number of games with their genres."""

    def __init__(self, genres: GenreRepo, games: GameRepo, http_fetcher: HttpAPIFetcher):
        self.genre_repo: GenreRepo = genres
        self.game_repo: GameRepo = games
        self.http_fetcher: HttpAPIFetcher = http_fetcher

    async def get_games_page(self, *, page: int = 1, page_size: int) -> RawgGamesPage:
        """Return one page of games. The next page is not requested."""
        payload = await self.http_fetcher.make_request(
            HTTPMethod.GET,
            'games',
            params=self._params({'page': page, 'page_size': page_size}),
        )
        return RawgGamesPage.model_validate(payload)

    async def get_game(self, game_id: int) -> RawgGameCard:
        """Return one game card."""
        payload = await self.http_fetcher.make_request(
            HTTPMethod.GET,
            f'games/{game_id}',
            params=self._params(),
        )
        return RawgGameCard.model_validate(payload)

    async def get_genre(self, genre_id: int) -> RawgGenreCard:
        """Return one genre card."""
        payload = await self.http_fetcher.make_request(
            HTTPMethod.GET,
            f'genres/{genre_id}',
            params=self._params(),
        )
        return RawgGenreCard.model_validate(payload)

    async def import_games(self, limit: int) -> None:
        """Create or update games from RAWG until limit results are read."""
        if limit < 1:
            msg = 'Game import limit must be positive'
            raise BadRequestError(msg)
        created_games = 0
        updated_games = 0
        created_genres = 0
        imported = 0
        page = 1
        while imported < limit:
            page_size = min(limit - imported, RAWG_MAX_PAGE_SIZE)
            data = await self.get_games_page(page=page, page_size=page_size)
            if not data.results:
                break
            for listed in data.results:
                if imported >= limit:
                    break
                created_genre_count, updated = await self._import_listed_game(listed)
                created_genres += created_genre_count
                if updated:
                    updated_games += 1
                else:
                    created_games += 1
                imported += 1
            if data.next is None:
                break
            page += 1
        logger.info(
            'RAWG import created %s games, updated %s games, created %s genres',
            created_games,
            updated_games,
            created_genres,
        )

    async def _import_listed_game(self, listed: RawgListedGame) -> tuple[int, bool]:
        genres, created_genres = await self._genres(listed)
        card = await self.get_game(listed.id)
        updated = await self._save_game(listed, card, genres)
        return created_genres, updated

    async def _genres(self, listed: RawgListedGame) -> tuple[list[Genre], int]:
        stored: dict[int, Genre] = {}
        created = 0
        for listed_genre in listed.genres:
            if listed_genre.id in stored:
                continue
            genre, was_created = await self._genre(listed_genre.id)
            stored[listed_genre.id] = genre
            if was_created:
                created += 1
        return sorted(stored.values(), key=lambda genre: genre.id), created

    async def _genre(self, rawg_id: int) -> tuple[Genre, bool]:
        external_id = str(rawg_id)
        found = await self.genre_repo.get_by_external(RAWG_SOURCE, external_id)
        if found is not None:
            return found, False
        card = await self.get_genre(rawg_id)
        return await self._store_genre(card.name, card.description, external_id)

    async def _store_genre(self, name: str, description: str | None, external_id: str) -> tuple[Genre, bool]:
        by_name = await self.genre_repo.get_by_name(name)
        if by_name is None:
            genre = Genre(
                id=await self.genre_repo.get_next_id(),
                name=name,
                description=description,
                external_source=RAWG_SOURCE,
                external_id=external_id,
            )
            await self.genre_repo.create(genre)
            return genre, True
        if by_name.external_source is None and by_name.external_id is None:
            stamped = by_name.model_copy(update={'external_source': RAWG_SOURCE, 'external_id': external_id})
            await self.genre_repo.update(stamped)
            return stamped, False
        msg = f'Genre with name={name} already exists'
        raise GenreNameAlreadyTakenError(msg)

    async def _save_game(self, listed: RawgListedGame, card: RawgGameCard, genres: list[Genre]) -> bool:
        description = card.description
        developer = card.developer
        publisher = card.publisher
        updated_at = datetime.now(settings.default_timezone)
        external_id = str(listed.id)
        existing = await self.game_repo.get_by_external(RAWG_SOURCE, external_id)
        if existing is None:
            await self.game_repo.create(
                Game(
                    id=await self.game_repo.get_next_id(),
                    uuid=uuid4(),
                    title=listed.name,
                    release_date=listed.released,
                    description=description,
                    metacritic=listed.metacritic,
                    developer=developer,
                    publisher=publisher,
                    is_published=True,
                    external_source=RAWG_SOURCE,
                    external_id=external_id,
                    genres=genres,
                    updated_at=updated_at,
                ),
            )
            return False
        await self.game_repo.update(
            existing.model_copy(
                update={
                    'title': listed.name,
                    'release_date': listed.released,
                    'description': description,
                    'metacritic': listed.metacritic,
                    'developer': developer,
                    'publisher': publisher,
                    'genres': genres,
                    'updated_at': updated_at,
                },
            ),
        )
        return True

    def _params(self, extra: dict[str, int] | None = None) -> dict[str, str | int]:
        params: dict[str, str | int] = {'key': rawg_settings.api_key.get_secret_value()}
        if extra is not None:
            params.update(extra)
        return params
