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
        self._responses: dict[tuple[str, str], list[object]] = {}

    def add_response(self, method: HTTPMethod, path: str, payload: object) -> None:
        """Remember a JSON body for this method and path.

        Several bodies are returned in the order they were added. The last body stays for
        further requests.
        """
        key = (method.value, path.lstrip('/'))
        self._responses.setdefault(key, []).append(payload)

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
        payloads = self._responses.get(key)
        if not payloads:
            msg = f'No local response for {method.value} {normalized}'
            raise LookupError(msg)
        if len(payloads) > 1:
            return payloads.pop(0)
        return payloads[0]
