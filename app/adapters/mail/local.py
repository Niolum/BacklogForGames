from typing import override

from domain.interfaces.mail import MailSender
from domain.models import MailMessage


class LocalMailSender(MailSender):
    """Mail sender for local development and tests."""

    @override
    async def send(self, message: MailMessage) -> None:
        """Skip delivery."""
