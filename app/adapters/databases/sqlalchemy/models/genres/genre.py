from __future__ import annotations
from typing import TYPE_CHECKING

from sqlalchemy import Index, Integer, Sequence, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from adapters.databases.sqlalchemy.db import Base
from adapters.databases.sqlalchemy.models.game_genres.game_genre import GameGenreORM
from domain.models import Genre


if TYPE_CHECKING:
    from adapters.databases.sqlalchemy.models.games.game import GameORM


class GenreORM(Base):
    """Genre model for SQLAlchemy."""

    __domain_model__ = Genre
    __tablename__ = 'genres'

    id: Mapped[int] = mapped_column(Integer, Sequence('genres_id_seq'), primary_key=True)
    name: Mapped[str] = mapped_column(Text, unique=True, index=True, nullable=False, comment='Genre name')
    description: Mapped[str | None] = mapped_column(Text, nullable=True, comment='Genre description')
    external_source: Mapped[str | None] = mapped_column(Text, nullable=True, comment='External catalog source')
    external_id: Mapped[str | None] = mapped_column(Text, nullable=True, comment='External catalog id')

    games: Mapped[list[GameORM]] = relationship(
        secondary=GameGenreORM.__table__,
        back_populates='genres',
    )

    __table_args__ = (
        Index(
            'ix_backlog_app_genres_external_source_external_id',
            'external_source',
            'external_id',
            unique=True,
        ),
    )
