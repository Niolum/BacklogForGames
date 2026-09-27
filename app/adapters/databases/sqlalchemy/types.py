from pathlib import Path
from typing import override

from sqlalchemy import Dialect, Text
from sqlalchemy.types import TypeDecorator


class PathType(TypeDecorator[Path]):
    """Store a path as text."""

    impl = Text
    cache_ok = True

    @override
    def process_bind_param(self, value: Path | None, dialect: Dialect) -> str | None:
        """Convert a path to text before writing it to the database."""
        if value is None:
            return None
        return str(value)

    @override
    def process_result_value(self, value: str | None, dialect: Dialect) -> Path | None:
        """Convert stored text back into a path."""
        if value is None:
            return None
        return Path(value)
