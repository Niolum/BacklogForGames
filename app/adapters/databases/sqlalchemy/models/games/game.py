from datetime import date
from pathlib import Path
from uuid import UUID

from sqlalchemy import Boolean, Date, Index, Integer, Sequence, Text, true
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import Mapped, mapped_column

from adapters.databases.sqlalchemy.db import Base
from adapters.databases.sqlalchemy.types import PathType
from domain.models import Game


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

    __table_args__ = (
        Index(
            'ix_backlog_app_games_external_source_external_id',
            'external_source',
            'external_id',
            unique=True,
        ),
    )
