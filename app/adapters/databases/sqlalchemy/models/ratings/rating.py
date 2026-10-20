from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index, Integer, Sequence, func
from sqlalchemy.orm import Mapped, mapped_column

from adapters.databases.sqlalchemy.db import Base
from domain.models import Rating


class RatingORM(Base):
    """User score for SQLAlchemy."""

    __domain_model__ = Rating
    __tablename__ = 'ratings'

    id: Mapped[int] = mapped_column(Integer, Sequence('ratings_id_seq'), primary_key=True)
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
        comment='User',
    )
    game_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey('games.id', ondelete='CASCADE'),
        nullable=False,
        comment='Game',
    )
    score: Mapped[int] = mapped_column(Integer, nullable=False, comment='Score from 1 to 10')
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

    __table_args__ = (
        Index(
            'ix_backlog_app_ratings_user_id_game_id',
            'user_id',
            'game_id',
            unique=True,
        ),
        CheckConstraint(
            'score >= 1 AND score <= 10',
            name='ck_backlog_app_ratings_score',
        ),
    )
