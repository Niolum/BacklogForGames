from http import HTTPMethod
from typing import override

import httpx

from domain.interfaces.http_fetcher import HttpAPIFetcher, HttpFile
from domain.logger import logger


class AsyncHttpAPIFetcher(HttpAPIFetcher):
    """HTTP client that sends requests with httpx."""

    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')

    @override
    async def download(self, url: str) -> HttpFile:
        logger.debug('HTTP GET %s', url)
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url)
                response.raise_for_status()
        except httpx.HTTPError as exc:
            msg = 'File download failed'
            raise LookupError(msg) from exc
        return HttpFile(content=response.content, content_type=response.headers.get('content-type'))

    @override
    async def make_request(
        self,
        method: HTTPMethod,
        path: str,
        json: dict[str, object] | None = None,
        headers: dict[str, str] | None = None,
        params: dict[str, str | int] | None = None,
        form_data: dict[str, str] | None = None,
        timeout: float | None = None,
    ) -> object:
        url = f'{self.base_url}/{path.lstrip("/")}'
        logger.debug('HTTP %s %s', method.value, path)
        async with httpx.AsyncClient() as client:
            response = await client.request(
                method.value,
                url,
                json=json,
                headers=headers,
                params=params,
                data=form_data,
                timeout=timeout,
            )
            response.raise_for_status()
            return response.json()
