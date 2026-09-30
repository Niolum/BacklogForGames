from abc import ABC, abstractmethod

from domain.models import MailMessage


class MailSender(ABC):
    """Port for sending email."""

    @abstractmethod
    async def send(self, message: MailMessage) -> None:
        """Send an email."""
