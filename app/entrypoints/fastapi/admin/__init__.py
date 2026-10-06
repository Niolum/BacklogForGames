from pathlib import Path

from fastapi import FastAPI
from sqladmin import Admin

from adapters.databases.sqlalchemy.db import engine
from config import settings
from .authentication import AdminAuthentication
from .mount import install_admin_mount_path


_TEMPLATES_DIR = Path(__file__).resolve().parent / 'templates'


def setup_admin(app: FastAPI) -> Admin:
    """Mount the admin panel. Routes stay closed until an administrator signs in."""
    authentication = AdminAuthentication(secret_key=settings.jwt_secret.get_secret_value())
    admin = Admin(
        app,
        engine,
        title=settings.project_name,
        authentication_backend=authentication,
        templates_dir=str(_TEMPLATES_DIR),
    )
    install_admin_mount_path(app)
    return admin
