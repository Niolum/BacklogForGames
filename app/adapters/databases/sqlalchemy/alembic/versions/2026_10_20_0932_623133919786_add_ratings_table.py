"""add ratings table

Revision ID: 623133919786
Revises: e7e69bc9f89a
Create Date: 2026-10-20 09:32:21.232229+00:00

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision: str = '623133919786'
down_revision: str | Sequence[str] | None = 'e7e69bc9f89a'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute(sa.text('CREATE SEQUENCE backlog_app.ratings_id_seq'))
    op.create_table(
        'ratings',
        sa.Column(
            'id',
            sa.Integer(),
            server_default=sa.text("nextval('backlog_app.ratings_id_seq'::regclass)"),
            nullable=False,
        ),
        sa.Column('user_id', sa.Integer(), nullable=False, comment='User'),
        sa.Column('game_id', sa.Integer(), nullable=False, comment='Game'),
        sa.Column('score', sa.Integer(), nullable=False, comment='Score from 1 to 10'),
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
            'score >= 1 AND score <= 10',
            name='ck_backlog_app_ratings_score',
        ),
        sa.ForeignKeyConstraint(['game_id'], ['backlog_app.games.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['backlog_app.users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        schema='backlog_app',
    )
    op.execute(sa.text('ALTER SEQUENCE backlog_app.ratings_id_seq OWNED BY backlog_app.ratings.id'))
    op.create_index(
        'ix_backlog_app_ratings_user_id_game_id',
        'ratings',
        ['user_id', 'game_id'],
        unique=True,
        schema='backlog_app',
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index('ix_backlog_app_ratings_user_id_game_id', table_name='ratings', schema='backlog_app')
    op.drop_table('ratings', schema='backlog_app')
