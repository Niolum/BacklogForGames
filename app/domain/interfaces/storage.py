from abc import ABC, abstractmethod
from pathlib import Path


class FileStorage(ABC):
    """Port for storing avatar and cover files."""

    @abstractmethod
    async def save(self, path: Path, content: bytes) -> None:
        """Store bytes at the relative path."""

    @abstractmethod
    async def delete(self, path: Path) -> None:
        """Remove the file. A missing file is not an error."""
