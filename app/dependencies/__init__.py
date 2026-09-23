from config import settings
from .container import DIContainer


def init_deps() -> DIContainer:
    """Инициализация DI"""
    deps = DIContainer()
    deps.config.from_pydantic(settings)
    return deps
