import asyncio
import smtplib
from email.message import EmailMessage
from typing import override

from domain.interfaces.mail import MailSender
from domain.models import MailMessage


class SMTPMailSender(MailSender):
    """Mail sender that delivers messages over SMTP."""

    def __init__(
        self,
        host: str,
        port: int,
        sender: str,
        username: str,
        password: str,
    ):
        self.host = host
        self.port = port
        self.sender = sender
        self.username = username
        self.password = password

    @override
    async def send(self, message: MailMessage) -> None:
        email = EmailMessage()
        email['From'] = self.sender
        email['To'] = message.recipient
        email['Subject'] = message.subject
        email.set_content(message.body)
        await asyncio.to_thread(self._deliver, email)

    def _deliver(self, email: EmailMessage) -> None:
        """Open an SMTP session and send the message."""
        with smtplib.SMTP_SSL(self.host, self.port, timeout=60) as smtp_server:
            smtp_server.login(self.username, self.password)
            smtp_server.send_message(email)
