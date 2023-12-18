"""Module with different base scheme"""

from pydantic import BaseModel


class HTTPNotFoundError(BaseModel):
    """Base sheme for not found exception"""

    detail: str

    class Config:
        json_schema_extra = {
            "example": {
                "detail": "Not Found",
            },
        }


class NotAuthenticatedError(BaseModel):
    """Base scheme for not authenticated exception"""

    detail: str

    class Config:
        json_schema_extra = {
            "example": {
                "detail": "Not authenticated",
            },
        }
