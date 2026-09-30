from datetime import UTC, datetime, timedelta

import pytest

from adapters.databases.in_memory.repositories.email_confirmations.email_confirmation import InMemEmailConfirmationRepo
from domain.exceptions import NotFoundError
from domain.models import EmailConfirmation


def _confirmation(**overrides) -> EmailConfirmation:
    data = {
        'id': 1,
        'user_id': 7,
        'token': 'confirm-token',
        'expires_at': datetime.now(UTC) + timedelta(hours=24),
    }
    return EmailConfirmation.model_validate(data | overrides)


async def test_email_confirmation_repo_finds_by_token() -> None:
    """The repository stores a confirmation and returns it by token."""
    repo = InMemEmailConfirmationRepo()
    confirmation = _confirmation()
    await repo.create(confirmation)

    assert await repo.get_by_token(confirmation.token) == confirmation
    assert await repo.get_by_token('missing') is None


async def test_email_confirmation_repo_updates_used_at() -> None:
    """Update stores the time when the token was used."""
    repo = InMemEmailConfirmationRepo()
    confirmation = _confirmation()
    await repo.create(confirmation)
    used_at = datetime.now(UTC)
    changed = confirmation.model_copy(update={'used_at': used_at})

    await repo.update(changed)

    stored = await repo.get_by_token(confirmation.token)
    assert stored is not None
    assert stored.used_at == used_at
    assert stored.user_id == confirmation.user_id


async def test_email_confirmation_repo_update_missing_raises() -> None:
    """Update of an unknown id raises not found."""
    repo = InMemEmailConfirmationRepo()

    with pytest.raises(NotFoundError, match='Email confirmation with id=1 not found'):
        await repo.update(_confirmation())
