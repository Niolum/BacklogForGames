"""add genres table

Revision ID: 2d6c9cd1e55a
Revises: 771594397690
Create Date: 2026-09-30 10:38:34.546709+00:00

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision: str = '2d6c9cd1e55a'
down_revision: str | Sequence[str] | None = '771594397690'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute(sa.text('CREATE SEQUENCE backlog_app.genres_id_seq'))
    op.create_table(
        'genres',
        sa.Column(
            'id',
            sa.Integer(),
            server_default=sa.text("nextval('backlog_app.genres_id_seq'::regclass)"),
            nullable=False,
        ),
        sa.Column('name', sa.Text(), nullable=False, comment='Genre name'),
        sa.Column('description', sa.Text(), nullable=True, comment='Genre description'),
        sa.Column('external_source', sa.Text(), nullable=True, comment='External catalog source'),
        sa.Column('external_id', sa.Text(), nullable=True, comment='External catalog id'),
        sa.PrimaryKeyConstraint('id'),
        schema='backlog_app',
    )
    op.execute(sa.text('ALTER SEQUENCE backlog_app.genres_id_seq OWNED BY backlog_app.genres.id'))
    op.create_index(
        'ix_backlog_app_genres_external_source_external_id',
        'genres',
        ['external_source', 'external_id'],
        unique=True,
        schema='backlog_app',
    )
    op.create_index(op.f('ix_backlog_app_genres_name'), 'genres', ['name'], unique=True, schema='backlog_app')


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_backlog_app_genres_name'), table_name='genres', schema='backlog_app')
    op.drop_index(
        'ix_backlog_app_genres_external_source_external_id',
        table_name='genres',
        schema='backlog_app',
    )
    op.drop_table('genres', schema='backlog_app')
