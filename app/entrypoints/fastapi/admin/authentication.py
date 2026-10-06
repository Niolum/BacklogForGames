from uuid import UUID

from pydantic import ValidationError
from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request

from domain.services import LoginData
from domain.use_cases import authenticate_admin, get_admin_user


class AdminAuthentication(AuthenticationBackend):
    """Session login for the admin panel.

    The form sends the email in the ``email`` field. A session is stored only
    for a confirmed user with ``is_admin``.
    """

    async def login(self, request: Request) -> bool:
        """Sign in an administrator and store their id in the session."""
        form = await request.form()
        email = _form_text(form.get('email'))
        password = _form_text(form.get('password'))
        if email is None or password is None:
            return False
        try:
            user_data = LoginData(email=email, password=password)
        except ValidationError:
            return False

        user = await authenticate_admin(user_data)
        if user is None:
            return False
        request.session.update({'user_id': str(user.uuid)})
        return True

    async def logout(self, request: Request) -> bool:
        """Drop the admin session."""
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        """Allow the request only while the session user is a confirmed administrator."""
        user_id = request.session.get('user_id')
        if not isinstance(user_id, str):
            return False
        try:
            user_uuid = UUID(user_id)
        except ValueError:
            return False
        user = await get_admin_user(user_uuid)
        return user is not None


def _form_text(value: object) -> str | None:
    """Return a form value when it is plain text."""
    if isinstance(value, str):
        return value
    return None
