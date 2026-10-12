from http import HTTPMethod, HTTPStatus

import httpx
import pytest

from adapters.http_fetchers import AsyncHttpAPIFetcher


async def test_async_http_fetcher_sends_one_request(monkeypatch: pytest.MonkeyPatch) -> None:
    """The real fetcher forwards the call to httpx and returns the JSON body."""
    timeout = 5.0
    calls: list[dict[str, object]] = []

    async def request(
        _self: httpx.AsyncClient,
        method: str,
        url: str,
        *,
        json: dict[str, object] | None = None,
        headers: dict[str, str] | None = None,
        params: dict[str, str | int] | None = None,
        data: dict[str, str] | None = None,
        timeout: float | None = None,
    ) -> httpx.Response:
        calls.append(
            {
                'method': method,
                'url': url,
                'json': json,
                'headers': headers,
                'params': params,
                'data': data,
                'timeout': timeout,
            },
        )
        return httpx.Response(HTTPStatus.OK, json={'ok': True}, request=httpx.Request(method, url))

    monkeypatch.setattr(httpx.AsyncClient, 'request', request)
    fetcher = AsyncHttpAPIFetcher('https://example.test/api/')
    body = await fetcher.make_request(
        HTTPMethod.POST,
        '/games',
        json={'title': 'Planescape'},
        headers={'Accept': 'application/json'},
        params={'page': 1},
        form_data={'file': 'cover'},
        timeout=timeout,
    )

    assert body == {'ok': True}
    assert len(calls) == 1
    sent = calls[0]
    assert sent['method'] == HTTPMethod.POST.value
    assert sent['url'] == 'https://example.test/api/games'
    assert sent['json'] == {'title': 'Planescape'}
    assert sent['headers'] == {'Accept': 'application/json'}
    assert sent['params'] == {'page': 1}
    assert sent['data'] == {'file': 'cover'}
    assert sent['timeout'] == timeout
