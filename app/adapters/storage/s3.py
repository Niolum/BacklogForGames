from pathlib import Path
from typing import override

from aioboto3.session import Session

from domain.exceptions import InvalidFilePath
from domain.interfaces.storage import FileStorage


class S3FileStorage(FileStorage):
    """File storage that keeps files in an S3 bucket."""

    def __init__(
        self,
        bucket: str,
        access_key: str,
        secret_key: str,
        endpoint_url: str | None = None,
    ):
        self.bucket = bucket
        self.access_key = access_key
        self.secret_key = secret_key
        self.endpoint_url = endpoint_url
        self._session = Session()

    @override
    async def save(self, path: Path, content: bytes) -> None:
        key = self._key(path)
        async with self._session.client(
            endpoint_url=self.endpoint_url,
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
            service_name='s3',
        ) as client:
            await client.put_object(Bucket=self.bucket, Key=key, Body=content)

    @override
    async def delete(self, path: Path) -> None:
        key = self._key(path)
        async with self._session.client(
            endpoint_url=self.endpoint_url,
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
            service_name='s3',
        ) as client:
            await client.delete_object(Bucket=self.bucket, Key=key)

    def _key(self, path: Path) -> str:
        """Return an object key. Absolute paths and parent segments are rejected."""
        if path.is_absolute() or '..' in path.parts:
            msg = 'Invalid file path'
            raise InvalidFilePath(msg)
        return path.as_posix()
