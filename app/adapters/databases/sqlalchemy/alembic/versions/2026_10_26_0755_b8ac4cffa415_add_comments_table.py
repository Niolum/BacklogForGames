"""add comments table

Revision ID: b8ac4cffa415
Revises: 623133919786
Create Date: 2026-10-26 07:55:19.791536+00:00

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision: str = 'b8ac4cffa415'
down_revision: str | Sequence[str] | None = '623133919786'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute(sa.text('CREATE SEQUENCE backlog_app.comments_id_seq'))
    op.create_table(
        'comments',
        sa.Column(
            'id',
            sa.Integer(),
            server_default=sa.text("nextval('backlog_app.comments_id_seq'::regclass)"),
            nullable=False,
        ),
        sa.Column('uuid', sa.UUID(), nullable=False, comment='Comment ID'),
        sa.Column('user_id', sa.Integer(), nullable=False, comment='User'),
        sa.Column('game_id', sa.Integer(), nullable=False, comment='Game'),
        sa.Column('text', sa.Text(), nullable=False, comment='Comment text'),
        sa.Column(
            'created_at',
            sa.DateTime(timezone=True),
            server_default=sa.text('now()'),
            nullable=False,
            comment='Record creation time',
        ),
        sa.Column(
            'updated_at',
            sa.DateTime(timezone=True),
            server_default=sa.text('now()'),
            nullable=False,
            comment='Record update time',
        ),
        sa.CheckConstraint(
            'char_length(text) >= 1 AND char_length(text) <= 1000',
            name='ck_backlog_app_comments_text',
        ),
        sa.ForeignKeyConstraint(['game_id'], ['backlog_app.games.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['backlog_app.users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        schema='backlog_app',
    )
    op.execute(sa.text('ALTER SEQUENCE backlog_app.comments_id_seq OWNED BY backlog_app.comments.id'))
    op.create_index(
        'ix_backlog_app_comments_uuid',
        'comments',
        ['uuid'],
        unique=True,
        schema='backlog_app',
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index('ix_backlog_app_comments_uuid', table_name='comments', schema='backlog_app')
    op.drop_table('comments', schema='backlog_app')
