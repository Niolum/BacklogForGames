"""add game genres and game timestamps

Revision ID: e135837f5644
Revises: f1b6b8b2c5a3
Create Date: 2026-10-07 10:17:53.964209+00:00

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision: str = 'e135837f5644'
down_revision: str | Sequence[str] | None = 'f1b6b8b2c5a3'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        'games',
        sa.Column(
            'created_at',
            sa.DateTime(timezone=True),
            server_default=sa.text('now()'),
            nullable=False,
            comment='Record creation time',
        ),
        schema='backlog_app',
    )
    op.add_column(
        'games',
        sa.Column(
            'updated_at',
            sa.DateTime(timezone=True),
            server_default=sa.text('now()'),
            nullable=False,
            comment='Record update time',
        ),
        schema='backlog_app',
    )
    op.create_table(
        'game_genres',
        sa.Column('game_id', sa.Integer(), nullable=False, comment='Game'),
        sa.Column('genre_id', sa.Integer(), nullable=False, comment='Genre'),
        sa.ForeignKeyConstraint(['game_id'], ['backlog_app.games.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['genre_id'], ['backlog_app.genres.id'], ondelete='RESTRICT'),
        sa.PrimaryKeyConstraint('game_id', 'genre_id'),
        schema='backlog_app',
    )
    op.create_index(
        'ix_backlog_app_game_genres_genre_id',
        'game_genres',
        ['genre_id'],
        unique=False,
        schema='backlog_app',
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index('ix_backlog_app_game_genres_genre_id', table_name='game_genres', schema='backlog_app')
    op.drop_table('game_genres', schema='backlog_app')
    op.drop_column('games', 'updated_at', schema='backlog_app')
    op.drop_column('games', 'created_at', schema='backlog_app')
