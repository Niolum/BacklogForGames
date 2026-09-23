from pydantic import BaseModel


class BaseRepo[DomainModel: BaseModel]:
    """Base repository"""
