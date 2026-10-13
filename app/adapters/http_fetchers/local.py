from http import HTTPMethod
from typing import override

from pydantic import BaseModel

from domain.interfaces.http_fetcher import HttpAPIFetcher


class LocalHttpCall(BaseModel):
    """One request seen by the local fetcher."""

    method: HTTPMethod
    path: str
    json_body: dict[str, object] | None
    headers: dict[str, str] | None
    params: dict[str, str | int] | None
    form_data: dict[str, str] | None
    timeout: float | None


class LocalHttpAPIFetcher(HttpAPIFetcher):
    """HTTP client that returns responses prepared in memory."""

    def __init__(self) -> None:
        self.calls: list[LocalHttpCall] = []
        self._responses: dict[tuple[str, str], object] = {}

    def add_response(self, method: HTTPMethod, path: str, payload: object) -> None:
        """Remember the JSON body returned for this method and path."""
        self._responses[(method.value, path.lstrip('/'))] = payload

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
        normalized = path.lstrip('/')
        self.calls.append(
            LocalHttpCall(
                method=method,
                path=normalized,
                json_body=json,
                headers=headers,
                params=params,
                form_data=form_data,
                timeout=timeout,
            ),
        )
        key = (method.value, normalized)
        if key not in self._responses:
            msg = f'No local response for {method.value} {normalized}'
            raise LookupError(msg)
        return self._responses[key]
