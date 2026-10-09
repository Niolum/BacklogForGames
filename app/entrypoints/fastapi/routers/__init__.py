from .auth import auth_router
from .game import game_router
from .genre import genre_router
from .user import user_router


__all__ = ['auth_router', 'game_router', 'genre_router', 'user_router']
