import inspect
from abc import ABC
from typing import Self

from domain.interfaces.repositories.base import BaseRepo
from domain.interfaces.uow import UnitOfWork


class BaseService(ABC):
    """Base service

    Provides a factory function for instantiating a service
    """

    __repos__: tuple[str, ...]

    def __init_subclass__(cls, **kwargs):
        cls.__repos__ = tuple(
            param.name
            for param in inspect.signature(cls.__init__).parameters.values()
            if issubclass(param.annotation, BaseRepo)
        )

    @classmethod
    def factory(cls, uow: UnitOfWork, *args, **kwargs) -> Self:
        """Factory method

        Creates a service instance initialized with all required repositories
        (based on the parameters in the actual repository's __init__ method)
        """
        repos = {repo_name: getattr(uow, repo_name) for repo_name in cls.__repos__}

        kwargs = repos | kwargs
        return cls(*args, **kwargs)
