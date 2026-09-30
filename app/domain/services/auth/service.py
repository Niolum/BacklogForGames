import secrets
from datetime import datetime
from uuid import uuid4

from config import settings
from domain.constants import EMAIL_CONFIRMATION_TOKEN_BYTES, EMAIL_CONFIRMATION_TTL
from domain.exceptions import AuthError, BacklogGamesConflictError, EmailAlreadyConfrimedError, EmailCofirmError
from domain.interfaces.mail import MailSender
from domain.interfaces.repositories import EmailConfirmationRepo, UserRepo
from domain.models import EmailConfirmation, MailMessage, User
from domain.services.base import BaseService
from .tokens import create_access_token, decode_access_token
from .types import CreateUserData, LoginData
from .utils import hash_password, verify_password


class AuthService(BaseService):
    """Service authentication for management registration, authentication and update tokens"""

    def __init__(
        self,
        users: UserRepo,
        email_confirmations: EmailConfirmationRepo,
        mail_sender: MailSender,
    ):
        self.user_repo: UserRepo = users
        self.email_confirmation_repo: EmailConfirmationRepo = email_confirmations
        self.mail_sender: MailSender = mail_sender

    async def register_user(self, user_data: CreateUserData) -> None:
        """Register new user"""
        db_user = await self.user_repo.get_by_email(user_data.email)
        if db_user:
            msg = f'User with email={user_data.email} already exists'
            raise BacklogGamesConflictError(msg)

        next_id = await self.user_repo.get_next_id()
        hashed_password = hash_password(user_data.password)

        user = User(
            id=next_id,
            uuid=uuid4(),
            nickname=user_data.nickname,
            email=user_data.email,
            password=hashed_password,
            email_confirmed=False,
            is_admin=False,
        )

        await self.user_repo.create(user)
        await self.send_confirmation_email(user)

    async def login(self, user_data: LoginData) -> str:
        """Issue an access token for a confirmed user."""
        user = await self.user_repo.get_by_email(user_data.email)
        if user is None or not verify_password(user_data.password, user.password):
            msg = 'Invalid email or password'
            raise AuthError(msg)
        if not user.email_confirmed:
            msg = 'Email is not confirmed'
            raise AuthError(msg)
        return create_access_token(user.uuid)

    async def get_current_user(self, token: str) -> User:
        """Return the user stored in a valid access token."""
        user_uuid = decode_access_token(token)
        return await self.user_repo.get_by_uuid_or_raise(user_uuid)

    async def resend_confirmation_email(self, email: str) -> None:
        """Send a new confirmation link when the email is still unconfirmed."""
        user = await self.user_repo.get_by_email_or_raise(email)
        if user.email_confirmed:
            msg = f'Email {email} is already confirmed'
            raise EmailAlreadyConfrimedError(msg)
        await self.send_confirmation_email(user)

    async def confirm_email(self, token: str) -> None:
        """Confirm the email when the token is unused and not expired."""
        confirmation = await self.email_confirmation_repo.get_by_token(token)
        now = datetime.now(settings.default_timezone)
        if confirmation is None or confirmation.used_at is not None or confirmation.expires_at <= now:
            msg = 'Confirmation token is invalid'
            raise EmailCofirmError(msg)

        user = await self.user_repo.get_by_id_or_raise(confirmation.user_id)

        await self.user_repo.update(user.model_copy(update={'email_confirmed': True}))
        await self.email_confirmation_repo.update(confirmation.model_copy(update={'used_at': now}))

    async def send_confirmation_email(self, user: User) -> None:
        """Create a confirmation token and send the link. The email stays unconfirmed."""
        confirmation_id = await self.email_confirmation_repo.get_next_id()
        token = secrets.token_urlsafe(EMAIL_CONFIRMATION_TOKEN_BYTES)
        confirmation = EmailConfirmation(
            id=confirmation_id,
            user_id=user.id,
            token=token,
            expires_at=datetime.now(settings.default_timezone) + EMAIL_CONFIRMATION_TTL,
        )
        await self.email_confirmation_repo.create(confirmation)
        link = f'{str(settings.public_base_url)}auth/confirm?token={token}'
        await self.mail_sender.send(
            MailMessage(
                recipient=user.email,
                subject='Confirm your email',
                body=f'Follow the link to confirm your email: {link}',
            ),
        )
