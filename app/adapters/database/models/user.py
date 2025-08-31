from datetime import date, datetime
from uuid import UUID

from sqlalchemy import Date, DateTime, Integer, Sequence, Text, func
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import Mapped, mapped_column

from adapters.database.db import Base
from domain.models import User


class UserORM(Base):
    """User model for SQLAlchemy"""

    __domain_model__ = User
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(Integer, Sequence('users_id_seq'), primary_key=True)
    uuid: Mapped[UUID] = mapped_column(
        postgresql.UUID(as_uuid=True),
        unique=True,
        index=True,
        nullable=False,
        comment='User ID',
    )
    nickname: Mapped[str] = mapped_column(Text, comment='User nickname')
    email: Mapped[str] = mapped_column(Text, comment='User email')
    password: Mapped[str] = mapped_column(Text, nullable=False)
    date_birth: Mapped[date | None] = mapped_column(Date, nullable=True, comment='Date of birth user')
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment='Date of registration user',
    )
    about: Mapped[str | None] = mapped_column(Text, nullable=True, comment='Information about yourself')
