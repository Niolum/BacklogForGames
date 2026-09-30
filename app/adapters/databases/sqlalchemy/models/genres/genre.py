from sqlalchemy import Index, Integer, Sequence, Text
from sqlalchemy.orm import Mapped, mapped_column

from adapters.databases.sqlalchemy.db import Base
from domain.models import Genre


class GenreORM(Base):
    """Genre model for SQLAlchemy."""

    __domain_model__ = Genre
    __tablename__ = 'genres'

    id: Mapped[int] = mapped_column(Integer, Sequence('genres_id_seq'), primary_key=True)
    name: Mapped[str] = mapped_column(Text, unique=True, index=True, nullable=False, comment='Genre name')
    description: Mapped[str | None] = mapped_column(Text, nullable=True, comment='Genre description')
    external_source: Mapped[str | None] = mapped_column(Text, nullable=True, comment='External catalog source')
    external_id: Mapped[str | None] = mapped_column(Text, nullable=True, comment='External catalog id')

    __table_args__ = (
        Index(
            'ix_backlog_app_genres_external_source_external_id',
            'external_source',
            'external_id',
            unique=True,
        ),
    )
