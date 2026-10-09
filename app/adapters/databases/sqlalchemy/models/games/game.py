from __future__ import annotations
from datetime import date, datetime
from pathlib import Path
from typing import TYPE_CHECKING, override
from uuid import UUID

from sqlalchemy import Boolean, Date, DateTime, Index, Integer, Sequence, Text, func, true
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import Mapped, mapped_column, relationship

from adapters.databases.sqlalchemy.db import Base
from adapters.databases.sqlalchemy.models.game_genres.game_genre import GameGenreORM
from adapters.databases.sqlalchemy.types import PathType
from domain.models import Game, Genre


if TYPE_CHECKING:
    from adapters.databases.sqlalchemy.models.genres.genre import GenreORM


class GameORM(Base):
    """Game model for SQLAlchemy."""

    __domain_model__ = Game
    __tablename__ = 'games'

    id: Mapped[int] = mapped_column(Integer, Sequence('games_id_seq'), primary_key=True)
    uuid: Mapped[UUID] = mapped_column(
        postgresql.UUID(as_uuid=True),
        unique=True,
        index=True,
        nullable=False,
        comment='Game ID',
    )
    title: Mapped[str] = mapped_column(Text, nullable=False, comment='Game title')
    release_date: Mapped[date | None] = mapped_column(Date, nullable=True, comment='Release date')
    cover_url: Mapped[Path | None] = mapped_column(PathType, nullable=True, comment='Cover URL')
    description: Mapped[str | None] = mapped_column(Text, nullable=True, comment='Game description')
    metacritic: Mapped[int | None] = mapped_column(Integer, nullable=True, comment='Metacritic score')
    developer: Mapped[str | None] = mapped_column(Text, nullable=True, comment='Developer')
    publisher: Mapped[str | None] = mapped_column(Text, nullable=True, comment='Publisher')
    is_published: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=true(),
        comment='Published in the catalog',
    )
    external_source: Mapped[str | None] = mapped_column(Text, nullable=True, comment='External catalog source')
    external_id: Mapped[str | None] = mapped_column(Text, nullable=True, comment='External catalog id')
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment='Record creation time',
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        comment='Record update time',
    )

    genres: Mapped[list[GenreORM]] = relationship(
        secondary=GameGenreORM.__table__,
        back_populates='games',
        lazy='selectin',
        order_by='GenreORM.id',
    )

    __table_args__ = (
        Index(
            'ix_backlog_app_games_external_source_external_id',
            'external_source',
            'external_id',
            unique=True,
        ),
    )

    @override
    async def to_domain(self) -> Game:
        """Domain game with its genres."""
        # game = super().to_domain()
        # genres = sorted(game.genres, key=lambda genre: genre.id)
        # return game.model_copy(update={'genres': genres})
        game = Game(
            id=self.id,
            uuid=self.uuid,
            title=self.title,
            release_date=self.release_date,
            cover_url=self.cover_url,
            description=self.description,
            metacritic=self.metacritic,
            developer=self.developer,
            publisher=self.publisher,
            is_published=self.is_published,
            external_source=self.external_source,
            external_id=self.external_id,
            created_at=self.created_at,
            updated_at=self.updated_at,
        )

        genre_orms: list[GenreORM] = await self.awaitable_attrs.genres

        genres = []
        for genre in genre_orms:
            genres.append(
                Genre(
                    id=genre.id,
                    name=genre.name,
                    description=genre.description,
                    external_source=genre.external_source,
                    external_id=genre.external_id,
                ),
            )
        game.genres = genres
        return game
