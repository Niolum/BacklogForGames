from pathlib import Path
from typing import override

import aiofiles
import aiofiles.os

from domain.exceptions import InvalidFilePath
from domain.interfaces.storage import FileStorage


class LocalFileStorage(FileStorage):
    """File storage that keeps files on the local disk."""

    def __init__(self, root: Path):
        self.root = root

    @override
    async def save(self, path: Path, content: bytes) -> None:
        target = self._resolve(path)
        await aiofiles.os.makedirs(target.parent, exist_ok=True)
        async with aiofiles.open(target, 'wb') as file:
            await file.write(content)

    @override
    async def delete(self, path: Path) -> None:
        target = self._resolve(path)
        try:
            await aiofiles.os.remove(target)
        except FileNotFoundError:
            return

    def _resolve(self, path: Path) -> Path:
        """Return an absolute path inside the storage root."""
        root = self.root.resolve()
        target = (root / path).resolve()
        if not target.is_relative_to(root):
            msg = 'Invalid file path'
            raise InvalidFilePath(msg)
        return target
