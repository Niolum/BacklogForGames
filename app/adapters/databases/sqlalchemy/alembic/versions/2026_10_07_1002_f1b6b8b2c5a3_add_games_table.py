"""add games table

Revision ID: f1b6b8b2c5a3
Revises: 2d6c9cd1e55a
Create Date: 2026-10-07 10:02:27.785511+00:00

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision: str = 'f1b6b8b2c5a3'
down_revision: str | Sequence[str] | None = '2d6c9cd1e55a'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute(sa.text('CREATE SEQUENCE backlog_app.games_id_seq'))
    op.create_table(
        'games',
        sa.Column(
            'id',
            sa.Integer(),
            server_default=sa.text("nextval('backlog_app.games_id_seq'::regclass)"),
            nullable=False,
        ),
        sa.Column('uuid', sa.UUID(), nullable=False, comment='Game ID'),
        sa.Column('title', sa.Text(), nullable=False, comment='Game title'),
        sa.Column('release_date', sa.Date(), nullable=True, comment='Release date'),
        sa.Column('cover_url', sa.Text(), nullable=True, comment='Cover URL'),
        sa.Column('description', sa.Text(), nullable=True, comment='Game description'),
        sa.Column('metacritic', sa.Integer(), nullable=True, comment='Metacritic score'),
        sa.Column('developer', sa.Text(), nullable=True, comment='Developer'),
        sa.Column('publisher', sa.Text(), nullable=True, comment='Publisher'),
        sa.Column(
            'is_published',
            sa.Boolean(),
            server_default=sa.text('true'),
            nullable=False,
            comment='Published in the catalog',
        ),
        sa.Column('external_source', sa.Text(), nullable=True, comment='External catalog source'),
        sa.Column('external_id', sa.Text(), nullable=True, comment='External catalog id'),
        sa.PrimaryKeyConstraint('id'),
        schema='backlog_app',
    )
    op.execute(sa.text('ALTER SEQUENCE backlog_app.games_id_seq OWNED BY backlog_app.games.id'))
    op.create_index(op.f('ix_backlog_app_games_uuid'), 'games', ['uuid'], unique=True, schema='backlog_app')
    op.create_index(
        'ix_backlog_app_games_external_source_external_id',
        'games',
        ['external_source', 'external_id'],
        unique=True,
        schema='backlog_app',
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(
        'ix_backlog_app_games_external_source_external_id',
        table_name='games',
        schema='backlog_app',
    )
    op.drop_index(op.f('ix_backlog_app_games_uuid'), table_name='games', schema='backlog_app')
    op.drop_table('games', schema='backlog_app')
