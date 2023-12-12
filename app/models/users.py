"""Module with User model"""

import uuid
from datetime import datetime

from sqlalchemy import String
from sqlalchemy.sql import func
from sqlalchemy.orm import Mapped, mapped_column

from app.services.database import Base


class User(Base):
    """SQL Model for user"""
    __tablename__ = "user"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    username: Mapped[str] = mapped_column(String(30), unique=True, index=True)
    first_name: Mapped[str | None] = mapped_column(String(60))
    last_name: Mapped[str | None] = mapped_column(String(60))
    avatar: Mapped[str | None]
    email: Mapped[str]
    hashed_password: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
