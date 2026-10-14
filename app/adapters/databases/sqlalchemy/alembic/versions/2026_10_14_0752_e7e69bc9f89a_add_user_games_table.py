"""add user games table

Revision ID: e7e69bc9f89a
Revises: e135837f5644
Create Date: 2026-10-14 07:52:31.334218+00:00

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision: str = 'e7e69bc9f89a'
down_revision: str | Sequence[str] | None = 'e135837f5644'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute(sa.text('CREATE SEQUENCE backlog_app.user_games_id_seq'))
    op.create_table(
        'user_games',
        sa.Column(
            'id',
            sa.Integer(),
            server_default=sa.text("nextval('backlog_app.user_games_id_seq'::regclass)"),
            nullable=False,
        ),
        sa.Column('user_id', sa.Integer(), nullable=False, comment='User'),
        sa.Column('game_id', sa.Integer(), nullable=False, comment='Game'),
        sa.Column('status', sa.String(length=16), nullable=False, comment='List status'),
        sa.Column(
            'created_at',
            sa.DateTime(timezone=True),
            server_default=sa.text('now()'),
            nullable=False,
            comment='Record creation time',
        ),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True, comment='Completion time'),
        sa.CheckConstraint(
            "status IN ('backlog', 'completed')",
            name='ck_backlog_app_user_games_status',
        ),
        sa.CheckConstraint(
            "status <> 'backlog' OR completed_at IS NULL",
            name='ck_backlog_app_user_games_backlog_completed_at',
        ),
        sa.ForeignKeyConstraint(['game_id'], ['backlog_app.games.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['backlog_app.users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        schema='backlog_app',
    )
    op.execute(sa.text('ALTER SEQUENCE backlog_app.user_games_id_seq OWNED BY backlog_app.user_games.id'))
    op.create_index(
        'ix_backlog_app_user_games_user_id_game_id',
        'user_games',
        ['user_id', 'game_id'],
        unique=True,
        schema='backlog_app',
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index('ix_backlog_app_user_games_user_id_game_id', table_name='user_games', schema='backlog_app')
    op.drop_table('user_games', schema='backlog_app')
