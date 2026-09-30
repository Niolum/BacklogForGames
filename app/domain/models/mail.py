from pydantic import BaseModel, EmailStr, Field


class MailMessage(BaseModel):
    """Outgoing email."""

    recipient: EmailStr = Field(description='Recipient email')
    subject: str = Field(description='Email subject')
    body: str = Field(description='Email body')
