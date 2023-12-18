"""Module with user's Exceptions"""


class NotFoundError(Exception):
    """Not found exception"""
    entity_name: str

    def __init__(self, entity_id):
        super().__init__(f"{self.entity_name} not found, id: {entity_id}")


class UserNotFoundError(NotFoundError):
    """User not found exception"""
    entity_name: str = "User"
