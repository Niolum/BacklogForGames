from pydantic import BaseModel, Field


class ErrorResponseSchema(BaseModel):
    """Error response"""

    detail: str = Field(description='Error description')
