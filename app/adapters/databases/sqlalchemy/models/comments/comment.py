from datetime import datetime
from uuid import UUID

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Integer, Sequence, Text, func
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import Mapped, mapped_column

from adapters.databases.sqlalchemy.db import Base
from domain.constants import COMMENT_TEXT_MAX_LENGTH, COMMENT_TEXT_MIN_LENGTH
from domain.models import Comment


class CommentORM(Base):
    """Comment for SQLAlchemy."""

    __domain_model__ = Comment
    __tablename__ = 'comments'

    id: Mapped[int] = mapped_column(Integer, Sequence('comments_id_seq'), primary_key=True)
    uuid: Mapped[UUID] = mapped_column(
        postgresql.UUID(as_uuid=True),
        unique=True,
        index=True,
        nullable=False,
        comment='Comment ID',
    )
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
    text: Mapped[str] = mapped_column(Text, nullable=False, comment='Comment text')
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
        CheckConstraint(
            f'char_length(text) >= {COMMENT_TEXT_MIN_LENGTH} AND char_length(text) <= {COMMENT_TEXT_MAX_LENGTH}',
            name='ck_backlog_app_comments_text',
        ),
    )
