from typing import ClassVar, Literal

from pydantic import BaseModel

from domain.logger import logger


class InMemBaseRepo[DomainModel: BaseModel]:
    """Base In-Memory Repository"""

    DB: ClassVar[dict]

    def _get(self, **kwargs) -> DomainModel | None:
        """Retrieve a single record"""
        for entity in self.DB.values():
            if all(getattr(entity, key) == value for key, value in kwargs.items()):
                return entity
        return None

    def _get_many(self, **kwargs) -> list[DomainModel]:
        """Get the list"""
        return [
            entity for entity in self.DB.values() if all(getattr(entity, key) == value for key, value in kwargs.items())
        ]

    async def get_by_id(self, pk) -> DomainModel | None:
        """Find by PK"""
        return self._get(id=pk)

    async def get_next_id(self) -> int:
        """Next ID"""
        return max(self.DB.keys() or [0]) + 1

    def _store(self, model: DomainModel, pk: str = 'id') -> None:
        """Save the model to the database"""
        self.__store_record(model, pk, 'create')

    def _update(self, model: DomainModel, pk: str = 'id') -> None:
        """Resave the model to the database"""
        self.__store_record(model, pk, 'update')

    def __store_record(self, model: DomainModel, pk: str, mode: Literal['create', 'update']):
        pk = getattr(model, pk)
        logger.debug(f'{mode.capitalize()} {model.__class__.__name__} (pk={pk or "Unknown"})')
        self.DB[pk] = model

    def _delete(self, model: DomainModel, pk: str = 'id') -> None:
        """Delete model from the database"""
        # self.DB[getattr(model, pk)] = model
