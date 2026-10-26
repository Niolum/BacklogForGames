"""add query indexes

Revision ID: f07e68c11e7b
Revises: b8ac4cffa415
Create Date: 2026-10-26 11:53:46.010024+00:00

"""

from collections.abc import Sequence

from alembic import op


# revision identifiers, used by Alembic.
revision: str = 'f07e68c11e7b'
down_revision: str | Sequence[str] | None = 'b8ac4cffa415'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_index(
        'ix_backlog_app_comments_game_id_created_at',
        'comments',
        ['game_id', 'created_at'],
        unique=False,
        schema='backlog_app',
    )
    op.create_index(
        'ix_backlog_app_ratings_game_id',
        'ratings',
        ['game_id'],
        unique=False,
        schema='backlog_app',
    )
    op.create_index(
        'ix_backlog_app_user_games_user_id_status',
        'user_games',
        ['user_id', 'status'],
        unique=False,
        schema='backlog_app',
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index('ix_backlog_app_user_games_user_id_status', table_name='user_games', schema='backlog_app')
    op.drop_index('ix_backlog_app_ratings_game_id', table_name='ratings', schema='backlog_app')
    op.drop_index('ix_backlog_app_comments_game_id_created_at', table_name='comments', schema='backlog_app')
