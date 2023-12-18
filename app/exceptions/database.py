"""Module with database Exceptions"""


class NotInitializedError(Exception):
    """Not Initialized exception"""
    entity_name: str

    def __init__(self):
        super().__init__(f"{self.entity_name}")


class DatabaseSessionManagerNotInitializedError(NotInitializedError):
    """DatabaseSessionManager Not Initialized exception"""
    entity_name: str = "DatabaseSessionManager is not initialized"
