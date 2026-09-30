from datetime import datetime
from uuid import UUID

import jwt

from config import settings
from domain.constants import ACCESS_TOKEN_TTL, JWT_ALGORITHM
from domain.exceptions import AuthError


def create_access_token(user_uuid: UUID) -> str:
    """Issue a signed access token for the user."""
    now = datetime.now(settings.default_timezone)
    payload = {'sub': str(user_uuid), 'iat': now, 'exp': now + ACCESS_TOKEN_TTL}
    return jwt.encode(payload, settings.jwt_secret.get_secret_value(), algorithm=JWT_ALGORITHM)


def decode_access_token(token: str) -> UUID:
    """Return the user uuid from a valid access token."""
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret.get_secret_value(),
            algorithms=[JWT_ALGORITHM],
        )
        return UUID(payload['sub'])
    except (jwt.PyJWTError, KeyError, TypeError, ValueError) as exc:
        msg = 'Invalid token'
        raise AuthError(msg) from exc
