from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, Enum, ForeignKey, Index, Integer, Sequence, func
from sqlalchemy.orm import Mapped, mapped_column

from adapters.databases.sqlalchemy.db import Base
from domain.models import UserGame, UserGameStatus


class UserGameORM(Base):
    """User list entry for SQLAlchemy."""

    __domain_model__ = UserGame
    __tablename__ = 'user_games'

    id: Mapped[int] = mapped_column(Integer, Sequence('user_games_id_seq'), primary_key=True)
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
    status: Mapped[UserGameStatus] = mapped_column(
        Enum(
            UserGameStatus,
            native_enum=False,
            create_constraint=False,
            length=16,
            values_callable=lambda statuses: [status.value for status in statuses],
        ),
        nullable=False,
        comment='List status',
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment='Record creation time',
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment='Completion time',
    )

    __table_args__ = (
        Index(
            'ix_backlog_app_user_games_user_id_game_id',
            'user_id',
            'game_id',
            unique=True,
        ),
        Index(
            'ix_backlog_app_user_games_user_id_status',
            'user_id',
            'status',
        ),
        CheckConstraint(
            "status IN ('backlog', 'completed')",
            name='ck_backlog_app_user_games_status',
        ),
        CheckConstraint(
            "status <> 'backlog' OR completed_at IS NULL",
            name='ck_backlog_app_user_games_backlog_completed_at',
        ),
    )
