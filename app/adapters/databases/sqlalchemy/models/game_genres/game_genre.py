from sqlalchemy import ForeignKey, Index, Integer
from sqlalchemy.orm import Mapped, mapped_column

from adapters.databases.sqlalchemy.db import Base
from domain.models import GameGenre


class GameGenreORM(Base):
    """Game and genre link for SQLAlchemy."""

    __domain_model__ = GameGenre
    __tablename__ = 'game_genres'

    game_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey('games.id', ondelete='CASCADE'),
        primary_key=True,
        comment='Game',
    )
    genre_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey('genres.id', ondelete='RESTRICT'),
        primary_key=True,
        comment='Genre',
    )

    __table_args__ = (Index('ix_backlog_app_game_genres_genre_id', 'genre_id'),)
