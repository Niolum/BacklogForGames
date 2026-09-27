from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, Sequence, Text
from sqlalchemy.orm import Mapped, mapped_column

from adapters.databases.sqlalchemy.db import Base
from domain.models import EmailConfirmation


class EmailConfirmationORM(Base):
    """Email confirmation model for SQLAlchemy."""

    __domain_model__ = EmailConfirmation
    __tablename__ = 'email_confirmations'

    id: Mapped[int] = mapped_column(Integer, Sequence('email_confirmations_id_seq'), primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
        comment='User',
    )
    token: Mapped[str] = mapped_column(Text, unique=True, index=True, nullable=False, comment='Confirmation token')
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        comment='Token expiration time',
    )
    used_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment='Token use time',
    )
