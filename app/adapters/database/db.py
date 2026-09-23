from typing import Self

from pydantic import BaseModel
from sqlalchemy import TEXT, MetaData, String
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from config import settings


engine = create_async_engine(
    str(settings.db_alembic_url),
    connect_args={
        'server_settings': {
            'search_path': settings.db_schema_name,
        },
    },
    echo=settings.db_echo,
    pool_pre_ping=True,
    pool_size=settings.alchemy_pool_size,
    max_overflow=settings.alchemy_pool_max_overflow,
)


async_session_maker = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
    autoflush=False,
    autobegin=False,
)


class Base[DomainModel: BaseModel](AsyncAttrs, DeclarativeBase):
    """Base class for models SQLAlchemy"""

    __domain_model__: type[DomainModel]

    metadata = MetaData(schema=settings.db_schema_name)
    type_annotation_map = {str: String().with_variant(TEXT, 'postgresql')}

    def to_domain(self) -> DomainModel:
        """Domain model"""
        if not self.__domain_model__:
            msg = 'No domain model defined'
            raise RuntimeError(msg)
        return self.__domain_model__.model_validate(self, from_attributes=True)

    @classmethod
    def from_model(cls, model: DomainModel) -> Self:
        """ORM model from domain model"""
        return cls(**model.model_dump(include=set(cls.__table__.columns.keys())))
