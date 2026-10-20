from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from domain.exceptions import AuthError
from domain.models import User
from domain.use_cases import get_current_user as load_current_user


_bearer = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer)],
) -> User:
    """Require an Authorization Bearer token and return the current user."""
    if credentials is None or credentials.scheme.lower() != 'bearer':
        msg = 'Not authenticated'
        raise AuthError(msg)
    return await load_current_user(credentials.credentials)


async def get_optional_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer)],
) -> User | None:
    """Return the current user when a Bearer token is present."""
    if credentials is None:
        return None
    return await load_current_user(credentials.credentials)


CurrentUser = Annotated[User, Depends(get_current_user)]
OptionalCurrentUser = Annotated[User | None, Depends(get_optional_user)]
