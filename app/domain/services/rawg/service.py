from http import HTTPMethod

from config import rawg_settings
from domain.interfaces.http_fetcher import HttpAPIFetcher
from domain.services.base import BaseService
from .types import RawgGameCard, RawgGamesPage, RawgGenreCard


class RawgService(BaseService):
    """Reads one RAWG page or one card through the HTTP fetcher."""

    def __init__(self, http_fetcher: HttpAPIFetcher):
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

    def _params(self, extra: dict[str, int] | None = None) -> dict[str, str | int]:
        params: dict[str, str | int] = {'key': rawg_settings.api_key.get_secret_value()}
        if extra is not None:
            params.update(extra)
        return params
