"""Module for Admin Panel"""

from sqladmin import ModelView

from app.models.users import User


class UserAdmin(ModelView, model=User):
    """Class User for Admin Panel"""
    column_list = [User.id, User.username]
