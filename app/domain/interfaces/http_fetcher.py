from abc import ABC, abstractmethod
from http import HTTPMethod

from pydantic import BaseModel


class HttpFile(BaseModel):
    """Bytes of one downloaded file."""

    content: bytes
    content_type: str | None = None


class HttpAPIFetcher(ABC):
    """Port for one HTTP request."""

    @abstractmethod
    async def download(self, url: str) -> HttpFile:
        """Download one file and return its bytes and content type."""

    @abstractmethod
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
        """Send one request and return the JSON body."""
