"""Module for authenticate in admin"""

from datetime import timedelta
from typing import Union

from fastapi import HTTPException, status, Request
from fastapi.responses import RedirectResponse
from sqladmin.authentication import AuthenticationBackend
from jose import JWTError, jwt

from app.depends import get_auth_service
from app.settings import setting


class AdminAuth(AuthenticationBackend):
    """Class for admin authentication"""
    auth_service = get_auth_service()

    def __init__(self, sessionmanager, secret_key):
        self.sessionmanager = sessionmanager
        super(AdminAuth, self).__init__(secret_key)

    async def login(self, request: Request) -> bool:
        form = await request.form()
        username, password = str(form["username"]), str(form["password"])
        async with self.sessionmanager.session() as session:
            user = await self.auth_service.authenticate_user(
                session,
                username,
                password
            )
        if not user:
            raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"}
        )
        if user.is_superuser is False:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission"
            )
        user_data = {
            "id": str(user.id),
            "username": user.username,
            "email": user.email
        }
        access_token_expires = timedelta(minutes=setting.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = self.auth_service.create_access_token(
            data={"sub": user.username}, expires_delta=access_token_expires
        )
        request.session.update({"token": access_token, "user": user_data})
        return True

    async def logout(self, request: Request) -> bool:
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> Union[bool, RedirectResponse]:
        user = request.session.get("user")
        if not user:
            redirect_uri = request.url_for('admin:login')
            return RedirectResponse(redirect_uri, status_code=302)

        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        token = request.session.get("token", None)
        try:
            payload = jwt.decode(token, setting.SECRET_KEY, algorithms=[setting.ALGORITHM])
            username: str | None = payload.get("sub")
            if username is None:
                raise credentials_exception
        except JWTError:
            raise credentials_exception

        return True
